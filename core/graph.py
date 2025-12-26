import os
import asyncio
import logging
from typing import Dict, Any, Literal
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

logger = logging.getLogger("GortexGraph")

def route_manager(state: GortexState) -> Literal["summarizer", "planner", "researcher", "analyst", "optimizer", "swarm", "evolution", "__end__"]:
    """Manager의 결정에 따라 다음 노드로 라우팅."""
    next_node = state.get("next_node", "__end__")
    logger.info(f"🛣️ [Router] Manager decided next_node: {next_node}")
    if next_node == "__end__":
        return "__end__"

    messages = state.get("messages", [])
    # 메시지가 없는 경우 토큰 계산 및 요약 로직 건너뛰기
    if not messages:
        return result_node(next_node)

    total_tokens = sum(count_tokens(m.content if hasattr(m, 'content') else str(m)) for m in messages)
    
    # [Dynamic Threshold] 백엔드 타입에 따른 동적 임계값 적용
    backend_type = os.getenv("LLM_BACKEND", "hybrid").lower()
    msg_threshold = 8 if backend_type == "ollama" else 15
    token_threshold = 3000 if backend_type == "ollama" else 10000
    
    if len(messages) >= msg_threshold or total_tokens >= token_threshold:
        logger.info(f"Triggering summarizer (Messages: {len(messages)}, Tokens: {total_tokens})")
        return "summarizer"
        
    # [Safety Breaker] 무한 루프 방지 (최대 25단계)
    step_count = state.get("step_count", 0)
    if step_count > 25:
        logger.warning(f"🛑 [Safety Breaker] Max steps reached ({step_count}). Forcing termination.")
        return "__end__"

    return result_node(next_node)

def result_node(next_node):
    result = "evolution" if next_node == "evolution" else next_node
    logger.info(f"🛣️ [Router] Manager routing to: {result}")
    return result

def route_after_summary(state: GortexState) -> str:
    """요약 후 원래 가려던 노드로 복귀"""
    result = state.get("next_node", "manager")
    logger.info(f"🛣️ [Router] Summarizer routing back to: {result}")
    return result

def route_coder(state: GortexState) -> Literal["coder", "analyst", "swarm", "manager"]:
    """Coder 노드의 다음 행방을 결정. 성공, 재시도, 에러, 반복 실패 대응."""
    messages = state.get("messages", [])
    if not messages:
        last_msg = ""
    else:
        last_msg = str(messages[-1][1] if isinstance(messages[-1], tuple) else messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1]))
    
    # 0. 병렬 작업 감지 (v6.0 New)
    if state.get("parallel_branches"):
        logger.info("🐉 Parallel branches detected. Routing to HydraNode.")
        return "hydra"

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


# [Hotfix] Sync Node Blocking Prevention
# 에이전트 내부의 동기식 LLM 호출(requests 등)이 메인 루프를 차단하지 않도록
# 별도 스레드에서 실행하는 비동기 래퍼를 적용합니다.

async def run_async_node(node_func, state: GortexState) -> Dict[str, Any]:
    node_name = node_func.__name__
    logger.info(f"🔄 [AsyncWrapper] Starting node: {node_name}")
    try:
        # [Safety Breaker] 실행 단계 카운트 증가
        state["step_count"] = state.get("step_count", 0) + 1
        
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, node_func, state)
        logger.info(f"✅ [AsyncWrapper] Finished node: {node_name} (Step: {state['step_count']})")
        return result
    except Exception as e:
        logger.error(f"❌ [AsyncWrapper] Failed node {node_name}: {e}")
        raise e

async def run_remote_node(node_name: str, state: GortexState) -> Dict[str, Any]:
    """노드를 원격 분산 워커에서 실행하고 결과를 반환함 (v5.3 Neural Auctioned)"""
    from gortex.core.mq import mq_bus
    
    # 1. 지능형 자원 경매 시작 (v5.3 New)
    target_worker = mq_bus.auction_task(node_name, dict(state))
    
    if not target_worker:
        logger.warning(f"⚠️ No suitable bidders for '{node_name}'. Falling back to local execution.")
        local_funcs = {"manager": manager_node, "planner": planner_node, "coder": coder_node, "analyst": analyst_node}
        return await run_async_node(local_funcs[node_name], state)

    logger.info(f"🌐 [NeuralAuction] Node '{node_name}' assigned to winner: {target_worker}")
    
    # 2. 원격 호출 (RPC)
    result = mq_bus.call_remote_node(node_name, dict(state))
    
    if result:
        return result
    else:
        logger.error(f"❌ [NeuralBalancer] {node_name} call to {target_worker} failed. Falling back.")
        local_funcs = {"manager": manager_node, "planner": planner_node, "coder": coder_node, "analyst": analyst_node}
        return await run_async_node(local_funcs[node_name], state)

# Async Wrappers (Remote-capable)
async def async_manager_node(state: GortexState):
    # 환경변수나 설정을 통해 특정 노드만 원격으로 보낼 수 있음
    if os.getenv("GORTEX_REMOTE_MANAGER") == "true":
        return await run_remote_node("manager", state)
    return await run_async_node(manager_node, state)

async def async_planner_node(state: GortexState):
    if os.getenv("GORTEX_REMOTE_PLANNER") == "true":
        return await run_remote_node("planner", state)
    return await run_async_node(planner_node, state)

async def async_coder_node(state: GortexState):
    # 코더는 리소스를 많이 소모하므로 분산 처리에 적합
    if os.getenv("GORTEX_REMOTE_CODER") == "true":
        return await run_remote_node("coder", state)
    return await run_async_node(coder_node, state)

async def async_researcher_node(state: GortexState): 
    return await run_async_node(researcher_node, state)

async def async_analyst_node(state: GortexState):
    if os.getenv("GORTEX_REMOTE_ANALYST") == "true":
        return await run_remote_node("analyst", state)
    return await run_async_node(analyst_node, state)

async def async_swarm_node(state: GortexState):
    return await run_async_node(swarm_node, state)

async def async_trend_scout_node(state: GortexState):
    return await run_async_node(trend_scout_node, state)

async def async_summarizer_node(state: GortexState):
    return await run_async_node(summarizer_node, state)

async def async_optimizer_node(state: GortexState):
    return await run_async_node(optimizer_node, state)

async def async_evolution_node(state: GortexState):
    return await run_async_node(evolution_node, state)

async def hydra_node(state: GortexState) -> Dict[str, Any]:
    """병렬 브랜치들을 동시에 실행하는 오케스트레이션 노드 (v6.0 Hydra Protocol)"""
    branches = state.get("parallel_branches", [])
    if not branches:
        return {"next_node": "coder"}

    from gortex.core.mq import mq_bus
    logger.info(f"🐉 [HydraNode] Spawning {len(branches)} parallel sub-workflows...")
    
    requests = []
    for b in branches:
        # 각 브랜치를 독립적인 실행 요청으로 구성
        sub_state = dict(state)
        sub_state["plan"] = b.get("steps", [])
        sub_state["assigned_persona"] = b.get("assigned_role", "standard")
        sub_state["current_step"] = 0
        
        # 병렬 실행을 위해 MQ 요청 리스트 생성
        requests.append(("coder", sub_state))

    # 병렬 호출 실행
    loop = asyncio.get_running_loop()
    results = await loop.run_in_executor(None, mq_bus.call_remote_nodes_parallel, requests)
    
    # 결과 집계
    combined_messages = []
    for res in results:
        combined_messages.extend(res.get("messages", []))
        
    logger.info(f"✅ [HydraNode] All {len(results)} branches merged.")
    
    return {
        "messages": combined_messages + [("ai", f"🐉 **하이드라 병합 완료**: {len(results)}개의 병렬 작업이 성공적으로 통합되었습니다.")],
        "next_node": "analyst", # 결과물 검증을 위해 Analyst로 보냄
        "parallel_branches": [] # 처리 완료 후 초기화
    }


def compile_gortex_graph(checkpointer=None):
    """Gortex 시스템의 모든 에이전트를 연결하여 그래프 컴파일"""
    from gortex.core.registry import registry
    workflow = StateGraph(GortexState)

    # 1. 노드 추가
    workflow.add_node("hydra", hydra_node) # 하이드라 노드 추가
    
    all_agents = registry.list_agents()
    logger.info(f"🕸️ Building graph with {len(all_agents)} registered agents...")
    
    for agent_name in all_agents:
        # 이미 래핑된 노드 함수가 있다면 사용 (하위 호환성)
        node_func_name = f"async_{agent_name.lower()}_node"
        current_module = globals()
        
        if node_func_name in current_module:
            workflow.add_node(agent_name.lower(), current_module[node_func_name])
        else:
            # 동적 래퍼 생성 (새로운 에이전트 대응)
            async def dynamic_node(state: GortexState, name=agent_name):
                from gortex.core.registry import registry
                agent_cls = registry.get_agent(name)
                if not agent_cls:
                    return {"next_node": "manager", "messages": [("system", f"Agent {name} not found.")]}
                instance = agent_cls()
                return await run_async_node(instance.run, state)
            
            workflow.add_node(agent_name.lower(), dynamic_node)

    # 2. 유틸리티 노드 추가 (Summarizer 등)
    workflow.add_node("summarizer", async_summarizer_node)
    workflow.add_node("optimizer", async_optimizer_node)
    workflow.add_node("evolution", async_evolution_node)

    # 3. 엣지 연결 (표준 워크플로우)
    workflow.add_edge(START, "manager")

    # Manager의 지능형 라우팅 (모든 등록된 에이전트로 전이 가능)
    routing_map = {name.lower(): name.lower() for name in all_agents}
    routing_map.update({
        "summarizer": "summarizer", "optimizer": "optimizer", 
        "evolution": "evolution", "__end__": END
    })
    
    workflow.add_conditional_edges("manager", route_manager, routing_map)

    # Summarizer 복귀 맵
    workflow.add_conditional_edges("summarizer", route_after_summary, routing_map)

    # 기본 수렴 에지
    for name in all_agents:
        if name.lower() not in ["manager", "coder"]:
            workflow.add_edge(name.lower(), "manager")

    # Planner -> Coder 특수 경로
    if "planner" in routing_map and "coder" in routing_map:
        workflow.add_edge("planner", "coder")

    # Coder 특수 라우팅
    workflow.add_conditional_edges(
        "coder",
        route_coder,
        {"coder": "coder", "analyst": "analyst", "swarm": "swarm", "manager": "manager"}
    )

    # Analyst -> Manager
    if "analyst" in routing_map:
        workflow.add_edge("analyst", "manager")

    # 그래프 컴파일
    if checkpointer is not None:
        return workflow.compile(checkpointer=checkpointer)
    else:
        # v3.0 표준: 실시간 복제를 지원하는 분산형 체크포인터 사용
        return workflow.compile(checkpointer=DistributedSaver())
