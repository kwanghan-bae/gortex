import os
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import aiosqlite

from gortex.core.state import GortexState
from gortex.agents.manager import manager_node
from gortex.agents.planner import planner_node
from gortex.agents.coder import coder_node
from gortex.agents.researcher import researcher_node
from gortex.agents.analyst import analyst_node
from gortex.agents.trend_scout import trend_scout_node

def route_manager(state: GortexState) -> Literal["planner", "researcher", "analyst", "__end__"]:
    """Manager의 결정에 따라 다음 노드로 라우팅"""
    return state.get("next_node", "__end__")

def route_coder(state: GortexState) -> Literal["coder", "manager", "__end__"]:
    """Coder의 작업 완료 여부에 따라 라우팅"""
    next_node = state.get("next_node", "manager")
    if next_node == "__end__":
        # 모든 step이 끝났다면 매니저에게 최종 확인을 받거나 종료
        return "manager"
    return "coder"

def compile_gortex_graph():
    """Gortex 시스템의 모든 에이전트를 연결하여 그래프 컴파일"""
    
    # 1. 그래프 생성
    workflow = StateGraph(GortexState)

    # 2. 노드 추가
    workflow.add_node("manager", manager_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("trend_scout", trend_scout_node)

    # 3. 엣지 연결
    # 시스템 시작 시 먼저 트렌드 스캔 수행
    workflow.add_edge(START, "trend_scout")
    workflow.add_edge("trend_scout", "manager")

    # Manager의 라우팅
    workflow.add_conditional_edges(
        "manager",
        route_manager,
        {
            "planner": "planner",
            "researcher": "researcher",
            "analyst": "analyst",
            "__end__": END
        }
    )

    # Planner -> Coder
    workflow.add_edge("planner", "coder")

    # Coder 루프 및 완료 후 Manager 복귀
    workflow.add_conditional_edges(
        "coder",
        route_coder,
        {
            "coder": "coder",
            "manager": "manager"
        }
    )

    # Researcher & Analyst 완료 후 Manager 복귀
    workflow.add_edge("researcher", "manager")
    workflow.add_edge("analyst", "manager")

    return workflow
