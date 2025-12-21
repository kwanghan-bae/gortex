from .base import AnalystAgent as BaseAnalyst
from .reflection import ReflectionAnalyst
from .organizer import WorkspaceOrganizer

class AnalystAgent(ReflectionAnalyst, WorkspaceOrganizer):
    """모든 분석 및 정리 기능이 통합된 최종 에이전트 클래스"""
    pass

# 기존 analyst_node는 통합 클래스를 사용하도록 유지
from gortex.core.state import GortexState
from typing import Dict, Any
import logging

logger = logging.getLogger("GortexAnalyst")

def analyst_node(state: GortexState) -> Dict[str, Any]:
    agent = AnalystAgent()
    from gortex.utils.translator import i18n
    
    # [Consensus] 토론 결과 처리
    if state.get("debate_context"):
        res = agent.synthesize_consensus("System Decision", state["debate_context"])
        msg = f"🤝 {i18n.t('analyst.consensus_reached', decision=res.get('final_decision', '')[:50])}"
        return {"messages": [("ai", msg)], "next_node": "manager"}

    return {"messages": [("ai", "분석을 종료합니다.")], "next_node": "manager"}
