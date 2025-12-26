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
                review_res = agent.perform_peer_review(state.get("review_target", "code"), last_ai_msg)
                score = review_res.get("score", 70)
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
        # 1. 지식 증류 및 전역 최적화 (Neural Distillation)
        if len(agent.memory.memory) > 10: 
            try: 
                from gortex.core.llm.distiller import distiller
                # 분야별 공인 지혜 증류 (Coding, Analysis 등)
                for cat in ["coding", "general"]:
                    wisdom = distiller.distill_wisdom(cat)
                    if wisdom:
                        logger.info(f"✨ Distilled new '최상위 원칙' for {cat.capitalize()}.")
                        agent.memory.save_rule(
                            instruction=wisdom,
                            trigger_patterns=[cat, "system", "rule"],
                            category=cat,
                            severity=5,
                            is_super_rule=True,
                            context=f"Neural Distillation from {cat} shard"
                        )
                
                # 2. 자가 학습 데이터셋 큐레이션 및 학습 트리거
                if datetime.now().hour % 12 == 0: 
                    dataset_path = distiller.prepare_training_dataset()
                    if dataset_path:
                        with open(dataset_path, 'r') as f:
                            sample_count = sum(1 for _ in f)
                        
                        if sample_count >= 50:
                            logger.info(f"🧠 Dataset reached {sample_count} samples. Triggering autonomous training!")
                            from gortex.core.llm.trainer import trainer
                            job_id = trainer.create_training_job(dataset_path)
                            trainer.start_job(job_id)
                            state["messages"].append(("system", f"🚀 **자가 학습 개시**: {sample_count}개의 데이터를 기반으로 SLM 학습을 시작합니다. (Job: {job_id})"))
            except Exception as e:
                logger.error(f"Intelligence refinement failed: {e}")

        # 3. 가비지 컬렉션 및 정적 최적화
        agent.garbage_collect_knowledge()
        agent.synthesize_global_rules()
            
        # 2. [Guardian Cycle] 선제적 결함 탐지 및 리팩토링 제안
        if energy > 85:
            logger.info("🛡️ Initiating Guardian Cycle: Scanning for proactive refactoring...")
            try:
                guardian_proposals = agent.propose_proactive_refactoring()
                if guardian_proposals:
                    # 가장 리스크가 높은 제안 하나를 선택하여 진행
                    top_p = guardian_proposals[0]
                    msg = f"🛡️ **가디언 모드 활성화**: 잠재적 결함이 발견되었습니다.\n\n**대상**: `{top_p['target_file']}`\n**이유**: {top_p['reason']}\n**기대 효과**: {top_p['expected_gain']}"
                    
                    # Swarm의 복구 모드와 유사한 흐름으로 Manager에게 전달
                    state["debate_result"] = {
                        "final_decision": f"Proactive Refactoring: {top_p['reason']}",
                        "action_plan": top_p["action_plan"]
                    }
                    
                    return {
                        "messages": [("ai", msg)],
                        "next_node": "manager",
                        "debate_result": state["debate_result"],
                        "agent_energy": energy - 15,
                        "is_guardian_mode": True # 선제적 최적화 모드 표시
                    }
            except Exception as e:
                logger.error(f"Guardian Cycle failed: {e}")

        # 3. 버전 관리 및 페르소나 진화 (기존 로직)
        if datetime.now().minute % 30 == 0:
            try:
                agent.generate_release_note()
                new_v = agent.bump_version()
                state["messages"].append(("system", f"🚀 **System Released**: Version {new_v} updated."))
                if datetime.now().hour % 6 == 0: 
                    agent.evolve_personas()
                agent.reinforce_successful_personas()
            except Exception:
                pass

        if len(agent.memory.memory) > 20: 
            try: 
                agent.memory.prune_memory()
            except Exception:
                pass
            
        try:
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
        except Exception: 
            pass

    return {"messages": [("ai", "분석을 마쳤습니다.")], "next_node": "manager"}
