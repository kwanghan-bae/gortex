import logging
import json
import os
import re
from typing import Dict, Any, List
from datetime import datetime
from gortex.core.state import GortexState
from gortex.utils.translator import i18n
from gortex.core.registry import registry
from gortex.utils.tools import read_file
from .base import AnalystAgent as BaseAnalyst
from .reflection import ReflectionAnalyst
from .organizer import WorkspaceOrganizer

logger = logging.getLogger("GortexAnalyst")

class AnalystAgent(ReflectionAnalyst, WorkspaceOrganizer):
    """모든 분석 및 정리 기능이 통합된 최종 에이전트 클래스"""
    @property
    def metadata(self):
        return BaseAnalyst().metadata

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
            import re
            json_match = re.search(r'{{.*}}', response_text, re.DOTALL)
            return json.loads(json_match.group(0)) if json_match else json.loads(response_text)
        except Exception as e:
            logger.error(f"Peer review failed: {e}")
            return {"score": 50, "comment": "Review failed", "is_approved": True}

# 레지스트리 등록 및 호환성 래퍼
analyst_instance = AnalystAgent()
registry.register("Analyst", AnalystAgent, analyst_instance.metadata)

def analyst_node(state: GortexState) -> Dict[str, Any]:
    """
    Analyst 노드 엔트리 포인트.
    코드 검증, 합의 도출, 데이터 분석 및 진화 로드맵 생성을 총괄합니다.
    """
    agent = analyst_instance
    
    # [MULTIMODAL - Priority 0] 시각 분석 결과 대기 중인 경우 최우선 처리
    if state.get("awaiting_visual_diagnosis"):
        logger.info("🧠 Performing multimodal visual analysis...")
        prompt = state.get("handoff_instruction", "Analyze the current UI state.")
        response = agent.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}])
        
        return {
            "messages": [("ai", f"👁️ **시각 분석 결과**:\n{response}")],
            "next_node": "manager",
            "awaiting_visual_diagnosis": False
        }

    # [Priority 1] 데이터 분석 및 시각적 이슈 감지
    last_msg_obj = state["messages"][-1]
    last_msg = last_msg_obj[1] if isinstance(last_msg_obj, tuple) else last_msg_obj.content
    
    # 시각적 이슈 감지
    visual_keywords = ["화면", "UI", "깨짐", "이상함", "screen", "glitch", "looks wrong"]
    if any(k in last_msg.lower() for k in visual_keywords):
        from gortex.utils.multimodal import capture_ui_screenshot
        screenshot_path = capture_ui_screenshot()
        logger.info(f"🎨 Visual issue detected. Analyzing screenshot: {screenshot_path}")
        
        analysis_msg = f"사용자가 시각적 이상을 보고했습니다. 다음 스크린샷을 분석하여 UI 결함이나 상태 이상이 있는지 진단하라. image:{screenshot_path}"
        
        return {
            "messages": [("ai", "📸 **시각적 진단 시작**: 현재 화면 상태를 캡처하여 분석 중입니다.")],
            "next_node": "analyst", 
            "handoff_instruction": analysis_msg,
            "awaiting_visual_diagnosis": True
        }

    data_files = [f for f in last_msg.split() if f.lower().endswith(('.csv', '.xlsx', '.json'))]
    if data_files:
        agent.analyze_data(data_files[0])
        return {"messages": [("ai", f"데이터 분석을 완료했습니다: {data_files[0]}")], "next_node": "manager"}

    # 1. 지식 베이스 최적화
    agent.garbage_collect_knowledge()
    agent.map_knowledge_relations()
    
    # 2. 아키텍처 감사
    violations = agent.audit_architecture()
    if violations:
        for v in violations:
            logger.warning(f"🛡️ [Architecture Drift] {v['reason']} ({v['source']} -> {v['target']})")
            
    try:
        prediction = agent.predict_architectural_bottleneck()
        if prediction.get("risk_level") == "High":
            state["messages"].append(("system", f"🔮 **Architecture Alert**: 건강도 하락이 예상됩니다. (예상 점수: {prediction['projected_score_3_sessions']})"))
    except Exception:
        pass

    # 3. 진화 로드맵
    try:
        roadmap = agent.generate_evolution_roadmap()
        if roadmap: 
            state["evolution_roadmap"] = roadmap 
    except Exception:
        pass

    debate_data = state.get("debate_context", [])

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

    # [Cross-Validation / Peer Review]
    if state.get("next_node") == "analyst" or state.get("awaiting_review"):
        ai_outputs = [m for m in state["messages"] if (isinstance(m, tuple) and m[0] == "ai") or (hasattr(m, 'type') and m.type == "ai")]
        if ai_outputs:
            last_ai_msg = ai_outputs[-1][1] if isinstance(ai_outputs[-1], tuple) else ai_outputs[-1].content
            val_res = agent.validate_constraints(state.get("active_constraints", []), {"content": last_ai_msg})
            
            if not val_res.get("is_valid", True):
                return {"messages": [("ai", f"🛡️ [Validation Alert] {val_res.get('reason')}")], "next_node": "planner"}
            
            if state.get("awaiting_review"):
                # 1. 기술적 품질 리뷰
                review_res = agent.perform_peer_review(state.get("review_target", "code"), last_ai_msg)
                score = review_res.get("score", 70)
                
                # 2. 헌장 준수 및 가치 정렬 검증 (Alignment Check)
                alignment_res = agent.validate_alignment_with_constitution(last_ai_msg)
                if not alignment_res.get("is_aligned", True):
                    msg = f"🛑 **Constitutional Violation**: 제안된 작업이 시스템 헌장을 위반합니다.\n\n**위반 사항**: {', '.join(alignment_res['violations'])}\n**조치**: {alignment_res['corrective_action']}"
                    return {
                        "messages": [("ai", msg)],
                        "next_node": "planner", 
                        "awaiting_review": False
                    }
                
                # 3. 오라클 루프: 선제적 장애 예측 (Pre-emptive Healing)
                oracle_res = agent.predict_runtime_errors(last_ai_msg, state.get("review_target", "unknown"))
                if oracle_res.get("risk_probability", 0) > 0.7:
                    msg = f"🔮 **장애 예지 활성화**: 런타임 오류 가능성({int(oracle_res['risk_probability']*100)}%)이 감지되었습니다.\n\n**예상 에러**: {oracle_res['predicted_error_type']}\n**사유**: {oracle_res['reason']}"
                    state["messages"].append(("system", msg))
                    self.ui.add_achievement("Oracle: Crash Prevented")
                    return {
                        "messages": [("ai", f"🛡️ **선제적 수리 개시**: 장애 방지를 위해 다음 조치를 취합니다: {oracle_res['preemptive_fix']}")],
                        "next_node": "coder",
                        "handoff_instruction": f"PREEMPTIVE_FIX: {oracle_res['preemptive_fix']}",
                        "awaiting_review": False
                    }

                if not review_res.get("is_approved", True) or score < 70:
                    issue_report = f"[CRITICAL ERROR DETECTED]\nType: Peer Review Rejected\nScore: {score}\nComment: {review_res.get('comment')}\nTarget: {state.get('review_target', 'Unknown')}"
                    return {
                        "messages": [("ai", f"🧐 [Peer Review Rejected] {review_res.get('comment')} (Score: {score})")], 
                        "next_node": "swarm",
                        "current_issue": issue_report,
                        "awaiting_review": False
                    }
                else:
                    state["messages"].append(("system", f"✅ [Peer Review Approved] {review_res.get('comment')} (Score: {review_res.get('score')})"))

            # [VISUAL VERIFICATION] 시각적 복구 모드인 경우 재캡처 및 검증
            if state.get("is_visual_recovery"):
                from gortex.utils.multimodal import capture_ui_screenshot
                new_screenshot = capture_ui_screenshot()
                analysis_msg = f"시각적 복구 작업 완료. image:{new_screenshot}"
                return {
                    "messages": [("ai", "👁️ **시각적 최종 검증 시작**: 수정 후 화면 상태를 분석 중입니다.")],
                    "next_node": "analyst",
                    "handoff_instruction": analysis_msg,
                    "awaiting_visual_diagnosis": True,
                    "is_visual_recovery": False 
                }

            # [GIT] 자율 커밋 및 병합
            active_branch = state.get("active_branch")
            if active_branch and score >= 90:
                from gortex.utils.git_tool import GitTool
                git = GitTool()
                try:
                    if git.is_repo():
                        git.add_all()
                        commit_msg = f"fix: 자율 복구 완료 (Score: {score})\n\nIssue: {state.get('current_issue', 'N/A')}"
                        git.commit(commit_msg)
                        git.checkout("main")
                        git.merge(active_branch)
                        state["messages"].append(("system", f"📦 **Git Auto-Merge**: `{active_branch}`가 `main`에 병합되었습니다."))
                except Exception: pass

            from gortex.utils.economy import get_economy_manager
            eco_manager = get_economy_manager()
            target_agent = state.get("review_target_agent", "Coder")
            quality = score / 100.0 if 'score' in locals() else 1.0
            difficulty = 3.0 if state.get("is_recovery_mode") else 1.5
            
            eco_manager.record_success(state, target_agent, quality_score=quality, difficulty=difficulty)
            eco_manager.update_skill_points(state, target_agent, category="Coding", quality_score=quality, difficulty=difficulty)
            
            return {
                "messages": [("ai", i18n.t("analyst.review_complete", risk_count=0))], 
                "agent_economy": state.get("agent_economy"), 
                "token_credits": state.get("token_credits"), 
                "next_node": "manager", 
                "awaiting_review": False,
                "is_recovery_mode": False
            }

    # [Self-Evolution & Guardian Cycle]
    energy = state.get("agent_energy", 100)
    if energy > 70 and not debate_data:
        # 1. [Security Analysis]
        last_security_alert = state.get("last_security_alert")
        if last_security_alert:
            defensive_rule = agent.generate_anti_failure_rule(last_security_alert["violation"], str(last_security_alert["payload"]))
            if defensive_rule:
                agent.memory.save_rule(defensive_rule["instruction"], defensive_rule["trigger_patterns"], category="general", severity=5, is_super_rule=True)
                state["messages"].append(("system", f"🛡️ **Neural Firewall Reinforced**: '{defensive_rule['instruction']}'"))
                state["last_security_alert"] = None

        # 2. [Swarm Expansion]
        if energy > 90 and state.get("coder_iteration", 0) > 5:
            agent_blueprint = agent.identify_capability_gap(error_log=str(state.get("messages", [])[-1]))
            if agent_blueprint:
                state["debate_result"] = {"final_decision": f"Spawn: {agent_blueprint['agent_name']}", "action_plan": ["Implement agent"], "agent_blueprint": agent_blueprint}
                return {"messages": [("ai", f"🧬 **에이전트 자가 증식**: '{agent_blueprint['agent_name']}' 설계 완료")], "next_node": "manager", "debate_result": state["debate_result"]}

        # 3. [ToolSmith Cycle]
        if energy > 80:
            last_failure = state.get("last_error_log")
            if last_failure:
                tool_blueprint = agent.identify_tool_gap(last_failure)
                if tool_blueprint:
                    state["debate_result"] = {"final_decision": f"Forge: {tool_blueprint['tool_name']}", "action_plan": ["Implement tool"]}
                    return {"messages": [("ai", f"🛠️ **도구 자가 증식**: '{tool_blueprint['tool_name']}' 제작 개시")], "next_node": "manager", "debate_result": state["debate_result"]}

        # 4. [Neural Distillation]
        if len(agent.memory.memory) > 10: 
            try: 
                from gortex.core.llm.distiller import distiller
                wisdom = distiller.distill_wisdom("coding")
                if wisdom:
                    agent.memory.save_rule(wisdom, ["code", "python"], category="coding", severity=5, is_super_rule=True)
                if datetime.now().hour % 12 == 0: distiller.prepare_training_dataset()
            except Exception: pass

        # 5. [Immune System]
        if energy > 80:
            try:
                infection_report = agent.scan_system_infection()
                if infection_report["status"] == "infected":
                    state["debate_result"] = {"final_decision": "Restore integrity", "action_plan": ["Rollback changes"]}
                    return {"messages": [("ai", "🚨 **면역 체계 반응 활성화**")], "next_node": "manager", "debate_result": state["debate_result"], "is_recovery_mode": True}
            except Exception: pass

        # 6. [Synaptic Mentoring]
        if energy > 85:
            try:
                all_agents = registry.list_agents()
                masters = [m for m in all_agents if state.get("agent_economy", {}).get(m.lower(), {}).get("level") in ["Gold", "Diamond"]]
                if masters:
                    syllabus = agent.create_mentoring_package(masters[0], "coding")
                    if syllabus: state["messages"].append(("system", f"👨‍🏫 **시냅스 멘토링 개시**: {masters[0]} 교육 패키지 생성"))
            except Exception: pass

        # 7. [Doc-Evolver]
        if energy > 60:
            try:
                agent.check_documentation_drift("gortex/core/state.py", "docs/TECHNICAL_SPEC.md", "GortexState")
            except Exception: pass

        # 8. [Sovereign Scaling]
        if energy > 80:
            try:
                scaling = agent.analyze_infrastructure_scaling(state)
                if scaling["should_scale"]:
                    from gortex.utils.infra import infra
                    infra.spawn_local_worker()
                    state["messages"].append(("system", "🏗️ **소버린 스케일링 활성화**"))
            except Exception: pass

        # 9. [Neural GC]
        if energy > 90 and len(registry.list_agents()) > 15:
            try:
                dormant = agent.identify_dormant_assets()
                for a_name in dormant.get("agents", []): registry.deregister(a_name)
            except Exception: pass

        agent.garbage_collect_knowledge()
        agent.synthesize_global_rules()

    return {"messages": [("ai", "분석을 마쳤습니다.")], "next_node": "manager"}