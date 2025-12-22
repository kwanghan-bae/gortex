import logging
import json
import os
import re
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
    
    def perform_peer_review(self, source_file: str, new_code: str, model_id: str = "gemini-1.5-flash") -> Dict[str, Any]:
        """다른 모델을 활용하여 생성된 코드의 품질을 교차 리뷰함"""
        prompt = f"""다음 리팩토링된 코드를 전문가의 시각에서 리뷰하라.
        
        [Target File] {source_file}
        [New Code]
        {new_code}
        
        가독성, 성능, 보안 위반 여부를 점검하고 100점 만점의 점수를 부여하라.
        결과는 반드시 JSON 형식을 따르라: {{ "score": int, "comment": "...", "is_approved": bool }}
        """
        try:
            response_text = self.backend.generate(model_id, [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            json_match = re.search(r'{{.*}}', response_text, re.DOTALL)
            return json.loads(json_match.group(0)) if json_match else json.loads(response_text)
        except Exception as e:
            logger.error(f"Peer review failed: {e}")
            return {"score": 50, "comment": "Review failed", "is_approved": True}

def analyst_node(state: GortexState) -> Dict[str, Any]:
    """
    Analyst 노드 엔트리 포인트.
    코드 검증, 합의 도출, 데이터 분석 및 진화 로드맵 생성을 총괄합니다.
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

    # 3. 진화 로드맵 생성
    roadmap = agent.generate_evolution_roadmap()
    if roadmap:
        state["evolution_roadmap"] = roadmap 

    last_msg_obj = state["messages"][-1]
    last_msg = last_msg_obj[1] if isinstance(last_msg_obj, tuple) else last_msg_obj.content
    last_msg_lower = last_msg.lower()
    
    debate_data = state.get("debate_context", [])
    data_files = [f for f in last_msg.split() if f.endswith(('.csv', '.xlsx', '.json'))]

    # [Consensus] Swarm으로부터 토론 결과가 넘어온 경우
    if debate_data and any(s.get("persona") for s in debate_data):
        res = agent.synthesize_consensus("High-Risk System Decision", debate_data)
        msg = f"🤝 **{i18n.t('analyst.consensus_reached', decision=res.get('final_decision', '')[:50])}**\n💡 Rationale: {res.get('rationale', 'N/A')}"
        
        history = state.get("consensus_history", [])
        history.append({"timestamp": datetime.now().isoformat(), "decision": res.get("final_decision")})
        return {
            "messages": [("ai", msg)],
            "next_node": "manager",
            "consensus_history": history,
            "debate_context": []
        }

    # [Cross-Validation / Peer Review] Coder 또는 Evolution의 결과 검증
    if state.get("next_node") == "analyst" or state.get("awaiting_review"):
        ai_outputs = [m for m in state["messages"] if (isinstance(m, tuple) and m[0] == "ai") or (hasattr(m, 'type') and m.type == "ai")]
        if ai_outputs:
            last_ai_msg = ai_outputs[-1][1] if isinstance(ai_outputs[-1], tuple) else ai_outputs[-1].content
            val_res = agent.validate_constraints(state.get("active_constraints", []), {"content": last_ai_msg})
            
            if not val_res.get("is_valid", True):
                return {"messages": [("ai", f"🛡️ [Validation Alert] {val_res.get('reason')}")], "next_node": "planner"}
            
            if state.get("awaiting_review"):
                review_res = agent.perform_peer_review(state.get("review_target", "code"), last_ai_msg)
                if not review_res.get("is_approved", True) or review_res.get("score", 100) < 70:
                    return {"messages": [("ai", f"🧐 [Peer Review Rejected] {review_res.get('comment')} (Score: {review_res.get('score')})")], "next_node": "coder"}
                else:
                    state["messages"].append(("system", f"✅ [Peer Review Approved] {review_res.get('comment')} (Score: {review_res.get('score')})"))

            economy = state.get("agent_economy", {}).copy()
            credits = state.get("token_credits", {}).copy()
            if "coder" not in economy: economy["coder"] = {"points": 0, "level": "Novice"}
            if "coder" not in credits: credits["coder"] = 100.0
            economy["coder"]["points"] += 10
            credits["coder"] += 10.0
            
            return {
                "messages": [("ai", i18n.t("analyst.review_complete", risk_count=0))], 
                "agent_economy": economy, "token_credits": credits, "next_node": "manager", "awaiting_review": False
            }

    # [Data Analysis]
    if data_files:
        res = agent.analyze_data(data_files[0])
        return {"messages": [("ai", i18n.t("analyst.data_analyzed", file=data_files[0]))], "next_node": "manager"}

    # [Self-Evolution]
    energy = state.get("agent_energy", 100)
    if energy > 70 and not debate_data and not data_files:
        if len(agent.memory.memory) > 30: agent.synthesize_global_rules()
            
        if datetime.now().minute % 30 == 0:
            agent.generate_release_note()
            new_v = agent.bump_version()
            state["messages"].append(("system", f"🚀 **System Released**: Version {new_v} updated."))
            if datetime.now().hour % 6 == 0: agent.evolve_personas()

        if len(agent.memory.memory) > 20: agent.memory.prune_memory()
            
        proposals = agent.propose_test_generation()
        if proposals:
            updates = {"messages": [], "agent_energy": energy - 10}
            for p in proposals:
                from gortex.utils.tools import write_file, execute_shell
                write_file(p["target_file"], p["content"])
                if "Ready to commit" in execute_shell(f"./scripts/pre_commit.sh --selective {p['target_file']}"):
                    updates["messages"].append(("ai", f"🧪 **테스트 자가 증식**: {p['target_file']} 생성 완료"))
                else:
                    if os.path.exists(p["target_file"]): os.remove(p["target_file"])
            if updates["messages"]:
                updates["next_node"] = "manager"
                return updates

    return {"messages": [("ai", "분석을 마쳤습니다.")], "next_node": "manager"}
