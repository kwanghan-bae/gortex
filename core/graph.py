import os
from typing import Literal
from langgraph.graph import StateGraph, START, END

from gortex.core.state import GortexState
from gortex.utils.token_counter import count_tokens
from gortex.agents.manager import manager_node
from gortex.agents.planner import planner_node
from gortex.agents.coder import coder_node
from gortex.agents.researcher import researcher_node
from gortex.agents.analyst import analyst_node
from gortex.agents.trend_scout import trend_scout_node
from gortex.agents.optimizer import optimizer_node
from gortex.agents.swarm import swarm_node
from gortex.agents.evolution_node import evolution_node
from gortex.utils.memory import summarizer_node
from gortex.core.persistence import DistributedSaver

import logging
logger = logging.getLogger("GortexGraph")

def route_manager(state: GortexState) -> Literal["summarizer", "planner", "researcher", "analyst", "optimizer", "swarm", "evolution", "__end__"]:
    """Manager의 결정에 따라 다음 노드로 라우팅."""
    next_node = state.get("next_node", "__end__")
    if next_node == "__end__":
        return "__end__"

    messages = state.get("messages", [])
    total_tokens = sum(count_tokens(m.content if hasattr(m, 'content') else str(m)) for m in messages)
    
    # [Dynamic Threshold] 백엔드 타입에 따른 동적 임계값 적용
    backend_type = os.getenv("LLM_BACKEND", "hybrid").lower()
    msg_threshold = 8 if backend_type == "ollama" else 15
    token_threshold = 3000 if backend_type == "ollama" else 10000
    
    if len(messages) >= msg_threshold or total_tokens >= token_threshold:
        logger.info(f"Triggering summarizer (Messages: {len(messages)}, Tokens: {total_tokens})")
        return "summarizer"
        
    return "evolution" if next_node == "evolution" else next_node

def route_after_summary(state: GortexState) -> str:
    """요약 후 원래 가려던 노드로 복귀"""
    return state.get("next_node", "manager")

def route_coder(state: GortexState) -> Literal["coder", "analyst", "swarm", "manager"]:
    """Coder 노드의 다음 행방을 결정. 성공, 재시도, 에러, 반복 실패 대응."""
    messages = state.get("messages", [])
    last_msg = str(messages[-1][1] if isinstance(messages[-1], tuple) else messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1]))
    
    # 1. 반복 실패 감지 -> Swarm 집단 지성 요청
    if state.get("coder_iteration", 0) > 3:
        logger.warning("🚑 Coder repeated failure. Escalating to Swarm Debug.")
        return "swarm"
        
    # 2. 긴급 에러 감지 -> Analyst 수술실행
    if "❌" in last_msg or "error" in last_msg.lower():
        logger.warning("🚨 Emergency detected. Routing to Surgeon (Analyst).")
        return "analyst"
        
    # 3. 기본 흐름 준수 (coder 또는 analyst)
    target = state.get("next_node", "coder")
    return target if target in ["coder", "analyst", "manager"] else "coder"

def compile_gortex_graph(checkpointer=None):
    """Gortex 시스템의 모든 에이전트를 연결하여 그래프 컴파일"""
    workflow = StateGraph(GortexState)

    # 노드 추가
    workflow.add_node("manager", manager_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("swarm", swarm_node)
    workflow.add_node("trend_scout", trend_scout_node)
    workflow.add_node("summarizer", summarizer_node)
    workflow.add_node("optimizer", optimizer_node)
    workflow.add_node("evolution", evolution_node)

    # 엣지 연결
    workflow.add_edge(START, "trend_scout")
    workflow.add_edge("trend_scout", "manager")

    # Manager의 라우팅
    workflow.add_conditional_edges(
        "manager",
        route_manager,
        {
            "summarizer": "summarizer",
            "planner": "planner",
            "researcher": "researcher",
            "analyst": "analyst",
            "optimizer": "optimizer",
            "swarm": "swarm",
            "evolution": "evolution",
            "__end__": END
        }
    )

    # Summarizer -> Target
    workflow.add_conditional_edges(
        "summarizer",
        route_after_summary,
        {
            "planner": "planner",
            "researcher": "researcher",
            "analyst": "analyst",
            "optimizer": "optimizer",
            "swarm": "swarm",
            "evolution": "evolution",
            "manager": "manager"
        }
    )

    # Swarm, Researcher, Optimizer, Evolution 완료 후 Manager 복귀
    workflow.add_edge("swarm", "manager")
    workflow.add_edge("researcher", "manager")
    workflow.add_edge("optimizer", "manager")
    workflow.add_edge("evolution", "manager")

    # Planner -> Coder
    workflow.add_edge("planner", "coder")

    # Coder 루프 및 완료 후 Analyst 검증 또는 Emergency Patch/Swarm Escalation
    workflow.add_conditional_edges(
        "coder",
        route_coder,
        {
            "coder": "coder",
            "analyst": "analyst",
            "swarm": "swarm",
            "manager": "manager"
        }
    )

    # Analyst 완료 후 Manager 복귀
    workflow.add_edge("analyst", "manager")

    # 그래프 컴파일
    if checkpointer is not None:
        return workflow.compile(checkpointer=checkpointer)
    else:
        # v3.0 표준: 실시간 복제를 지원하는 분산형 체크포인터 사용
        return workflow.compile(checkpointer=DistributedSaver())