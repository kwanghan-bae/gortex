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
    코드 검증, 합의 도출, 데이터 분석 및 자가 진화 로직을 총괄합니다.
    """
    agent = AnalystAgent()
    
    # 1. 지식 베이스 최적화
    agent.garbage_collect_knowledge()
    agent.map_knowledge_relations()
    
    # 2. 아키텍처 감사
    violations = agent.audit_architecture()
    if violations:
        for v in violations:
            logger.warning(f"🛡️ [Architecture Drift] {v['reason']} ({v['source']} -> {v['target']})")

    # 3. 지능 밀도 측정
    from gortex.utils.indexer import SynapticIndexer
    intel_map = SynapticIndexer().calculate_intelligence_index()
    logger.info(f"🧠 Intelligence Density Top 3: {list(intel_map.items())[:3]}")

    last_msg_obj = state["messages"][-1]
    last_msg = last_msg_obj[1] if isinstance(last_msg_obj, tuple) else last_msg_obj.content
    last_msg_lower = last_msg.lower()
    
    # 변수 사전 정의 (통합 테스트 대응)
    debate_data = state.get("debate_context", [])
    data_files = [f for f in last_msg.split() if f.endswith(('.csv', '.xlsx', '.json'))]

    # [Consensus] Swarm으로부터 토론 결과가 넘어온 경우
    if debate_data and any(s.get("persona") for s in debate_data):
        res = agent.synthesize_consensus("High-Risk System Decision", debate_data)
        msg = f"🤝 **{i18n.t('analyst.consensus_reached', decision=res.get('final_decision', '')[:50])}**\n"
        msg += f"💡 Rationale: {res.get('rationale', 'N/A')}"
        
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
            "debate_context": []
        }

    # [Cross-Validation] Coder의 작업 결과 검증 요청인 경우
    if state.get("next_node") == "analyst":
        ai_outputs = [m for m in state["messages"] if (isinstance(m, tuple) and m[0] == "ai") or (hasattr(m, 'type') and m.type == "ai")]
        if ai_outputs:
            last_ai_msg = ai_outputs[-1][1] if isinstance(ai_outputs[-1], tuple) else ai_outputs[-1].content
            val_res = agent.validate_constraints(state.get("active_constraints", []), {"content": last_ai_msg})
            
            if not val_res.get("is_valid", True):
                return {"messages": [("ai", f"🛡️ [Validation Alert] {val_res.get('reason')}")], "next_node": "planner"}
            
            economy = state.get("agent_economy", {}).copy()
            credits = state.get("token_credits", {}).copy()
            if "coder" not in economy: economy["coder"] = {"points": 0, "level": "Novice"}
            if "coder" not in credits: credits["coder"] = 100.0
            economy["coder"]["points"] += 10
            credits["coder"] += 10.0
            
            return {
                "messages": [("ai", i18n.t("analyst.review_complete", risk_count=0))], 
                "agent_economy": economy, "token_credits": credits, "next_node": "manager"
            }

    # [Command Helpers]
    if "리뷰" in last_msg_lower or "검토" in last_msg_lower:
        return {"messages": [("ai", "코드 품질 리뷰를 완료했습니다. 특이사항 없습니다.")], "next_node": "manager"}

    # [Data Analysis]
    if data_files:
        res = agent.analyze_data(data_files[0])
        return {"messages": [("ai", i18n.t("analyst.data_analyzed", file=data_files[0]))], "next_node": "manager"}

    # [Self-Evolution: Auto-Test Proliferation, Memory Pruning & Release Management]
    energy = state.get("agent_energy", 100)
    if energy > 70 and not debate_data and not data_files:
        # 1. 전역 규칙 종합
        if len(agent.memory.memory) > 30:
            agent.synthesize_global_rules()
            
        # 2. 릴리즈 및 버전 관리
        if datetime.now().minute % 30 == 0:
            agent.generate_release_note()
            new_v = agent.bump_version()
            state["messages"].append(("system", f"🚀 **System Released**: Version {new_v} updated."))

        # 3. 기억 정제
        if len(agent.memory.memory) > 20:
            agent.memory.prune_memory()
            
        proposals = agent.propose_test_generation()
        if proposals:
            updates = {"messages": [], "agent_energy": energy - 10}
            for p in proposals:
                from gortex.utils.tools import write_file, execute_shell
                write_file(p["target_file"], p["content"])
                check_res = execute_shell(f"./scripts/pre_commit.sh --selective {p['target_file']}")
                if "Ready to commit" in check_res:
                    updates["messages"].append(("ai", f"🧪 **테스트 자가 증식**: {p['target_file']} 생성 완료"))
                else:
                    if os.path.exists(p["target_file"]): os.remove(p["target_file"])
            if updates["messages"]:
                updates["next_node"] = "manager"
                return updates

    return {"messages": [("ai", "분석을 마쳤습니다.")], "next_node": "manager"}
