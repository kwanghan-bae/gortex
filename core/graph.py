import os
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import aiosqlite

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
from gortex.utils.memory import summarizer_node

def route_manager(state: GortexState) -> Literal["summarizer", "planner", "researcher", "analyst", "optimizer", "swarm", "__end__"]:
    """Manager의 결정에 따라 다음 노드로 라우팅."""
    next_node = state.get("next_node", "__end__")
    if next_node == "__end__":
        return "__end__"

    messages = state.get("messages", [])
    total_tokens = sum(count_tokens(m.content if hasattr(m, 'content') else str(m)) for m in messages)
    
    if len(messages) >= 12 or total_tokens >= 5000:
        return "summarizer"
        
    return next_node

def route_after_summary(state: GortexState) -> str:
    """요약 후 원래 가려던 노드로 복귀"""
    return state.get("next_node", "manager")

def route_coder(state: GortexState) -> Literal["coder", "analyst", "__end__"]:
    """Coder의 작업 완료 여부에 따라 라우팅 (Cross-Validation 단계 추가)"""
    next_node = state.get("next_node", "manager")
    if next_node == "__end__":
        # 모든 step이 끝났다면 즉시 manager로 가지 않고 analyst 검증을 거침
        return "analyst"
    return "coder"

def compile_gortex_graph():
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
            "manager": "manager"
        }
    )

    # Swarm 완료 후 Manager 복귀
    workflow.add_edge("swarm", "manager")

    # Planner -> Coder
    workflow.add_edge("planner", "coder")

    # Coder 루프 및 완료 후 Analyst(Cross-Validation) 거쳐 Manager 복귀
    workflow.add_conditional_edges(
        "coder",
        route_coder,
        {
            "coder": "coder",
            "analyst": "analyst"
        }
    )

    # Analyst 완료 후 Manager 복귀
    workflow.add_edge("analyst", "manager")

    # Researcher & Optimizer 완료 후 Manager 복귀
    workflow.add_edge("researcher", "manager")
    workflow.add_edge("optimizer", "manager")

    # 그래프 컴파일 (체크포인터 추가)
    from langgraph.checkpoint.memory import MemorySaver
    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)
