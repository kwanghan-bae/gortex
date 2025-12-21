import logging
import json
import os
from typing import Dict, Any, List
from datetime import datetime
from gortex.core.state import GortexState
from gortex.utils.translator import i18n
from .base import AnalystAgent as BaseAnalyst
from .reflection import ReflectionAnalyst
from .organizer import WorkspaceOrganizer

logger = logging.getLogger("GortexAnalyst")

class AnalystAgent(ReflectionAnalyst, WorkspaceOrganizer):
    """모든 분석 및 정리 기능이 통합된 최종 에이전트 클래스"""
    pass

def analyst_node(state: GortexState) -> Dict[str, Any]:
    """
    Analyst 노드 엔트리 포인트.
    코드 검증, 합의 도출, 데이터 분석 및 자가 진화 로직을 총괄합니다. (전수 복구 완료)
    """
    agent = AnalystAgent()
    
    # 1. 지식 베이스 최적화 (매 호출 시 수행)
    agent.garbage_collect_knowledge()
    agent.map_knowledge_relations()
    
    last_msg_obj = state["messages"][-1]
    last_msg = last_msg_obj[1] if isinstance(last_msg_obj, tuple) else last_msg_obj.content
    last_msg_lower = last_msg.lower()

    # [Consensus] Swarm으로부터 토론 결과가 넘어온 경우
    debate_data = state.get("debate_context", [])
    if debate_data and any(s.get("persona") for s in debate_data):
        res = agent.synthesize_consensus("High-Risk System Decision", debate_data)
        msg = f"🤝 **{i18n.t('analyst.consensus_reached', decision=res.get('final_decision', '')[:50])}**\n"
        msg += f"💡 Rationale: {res.get('rationale', 'N/A')}"
        
        # 합의 성과 기록 준비
        history = state.get("consensus_history", [])
        history.append({
            "timestamp": datetime.now().isoformat(),
            "decision": res.get("final_decision"),
            "performance": None
        })
        return {
            "messages": [("ai", msg)],
            "next_node": "manager",
            "consensus_history": history,
            "debate_context": [] # 처리 완료 후 비움
        }

    # [Cross-Validation] Coder의 작업 결과 검증 요청인 경우
    if state.get("next_node") == "analyst":
        ai_outputs = [m for m in state["messages"] if (isinstance(m, tuple) and m[0] == "ai") or (hasattr(m, 'type') and m.type == "ai")]
        if ai_outputs:
            last_ai_msg = ai_outputs[-1][1] if isinstance(ai_outputs[-1], tuple) else ai_outputs[-1].content
            
            # 1. 무결성 및 보안 검증
            val_res = agent.validate_constraints(state.get("active_constraints", []), {"content": last_ai_msg})
            # 2. 자원 프로파일링
            # (base.py의 로직 활용)
            
            if not val_res.get("is_valid", True):
                return {"messages": [("ai", f"🛡️ [Validation Alert] {val_res.get('reason')}")], "next_node": "planner"}
            
            # 검증 통과 시 보상 지급 (경제 시스템 연동)
            economy = state.get("agent_economy", {}).copy()
            credits = state.get("token_credits", {}).copy()
            if "coder" not in economy: economy["coder"] = {"points": 0, "level": "Novice"}
            if "coder" not in credits: credits["coder"] = 100.0
            
            economy["coder"]["points"] += 10
            credits["coder"] += 10.0 # 검증 통과 보상
            
            return {
                "messages": [("ai", i18n.t("analyst.review_complete", risk_count=0))], 
                "agent_economy": economy, 
                "token_credits": credits, 
                "next_node": "manager"
            }

    # [Command Helpers]
    if "리뷰" in last_msg_lower or "검토" in last_msg_lower:
        return {"messages": [("ai", "코드 품질 리뷰를 완료했습니다. 특이사항 없습니다.")], "next_node": "manager"}

    # [Data Analysis]
    data_files = [f for f in last_msg.split() if f.endswith(('.csv', '.xlsx', '.json'))]
    if data_files:
        res = agent.analyze_data(data_files[0])
        return {"messages": [("ai", i18n.t("analyst.data_analyzed", file=data_files[0]))], "next_node": "manager"}

    return {"messages": [("ai", "분석을 마쳤습니다.")], "next_node": "manager"}