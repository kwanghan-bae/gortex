import logging
import json
import os
import time
import re
from typing import Dict, Any
from gortex.core.state import GortexState
from gortex.core.llm.factory import LLMFactory
from gortex.utils.log_vectorizer import SemanticLogSearch
from gortex.utils.translator import SynapticTranslator
from gortex.utils.vector_store import LongTermMemory
from gortex.utils.efficiency_monitor import EfficiencyMonitor
from gortex.core.registry import registry, AgentMetadata
from gortex.agents.base import BaseAgent

logger = logging.getLogger("GortexManager")

class ManagerAgent(BaseAgent):
    """
    Gortex 시스템의 중앙 관제소(Manager) 에이전트.
    의도 분석, 에이전트 탐색, 모델 할당 및 시스템 확장을 총괄합니다.
    """
    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="Manager",
            role="Orchestrator",
            description="Analyzes intent, discovers capabilities, and scales the system autonomously.",
            tools=["route_task", "allocate_resources", "manage_expansion"],
            version="3.0.0"
        )

    def run(self, state: GortexState) -> Dict[str, Any]:
        log_search = SemanticLogSearch()
        translator = SynapticTranslator()
        ltm = LongTermMemory()
        monitor = EfficiencyMonitor()
        start_time = time.time()
        
        # 1. 언어 감지 및 번역
        last_msg_obj = state["messages"][-1]
        raw_input = (last_msg_obj[1] if isinstance(last_msg_obj, tuple) else last_msg_obj.content).strip()
        
        # [OPTIMIZATION] 단순 인사말 필터링 (LLM 호출 없이 즉시 응답)
        greetings = ["안녕", "hi", "hello", "반가워", "누구니", "help"]
        if any(g in raw_input.lower() for g in greetings) and len(raw_input) < 10:
            return {
                "thought": "사용자의 단순 인사말에 즉시 응답합니다.",
                "next_node": "__end__",
                "messages": [("ai", "안녕하세요! Gortex입니다. 무엇을 도와드릴까요? 도움말이 필요하시면 /help를 입력해주세요.")]
            }

        lang_info = translator.detect_and_translate(raw_input)
        internal_input = lang_info.get("translated_text", raw_input) if not lang_info.get("is_korean") else raw_input

        energy = state.get("agent_energy", 100)
        roadmap = state.get("evolution_roadmap", [])

        # 2. Swarm 토론 및 Guardian Cycle 결과 처리 (합의안을 계획으로 전환)
        debate_res = state.get("debate_result")
        if debate_res and debate_res.get("action_plan"):
            is_recovery = state.get("is_recovery_mode", False)
            is_guardian = state.get("is_guardian_mode", False)
            
            mode_title = "🩺 **긴급 복구 모드 활성화**" if is_recovery else "🛡️ **선제적 가디언 모드 활성화**"
            mode_desc = "Swarm 합의안" if not is_guardian else "가디언 최적화 안"
            
            logger.info(f"⚖️ Translating {mode_desc} into executable plan...")
            action_plan = debate_res["action_plan"]
            
            new_plan = []
            for step in action_plan:
                new_plan.append(json.dumps({
                    "action": "execute_shell" if any(k in step.lower() for k in ["run", "test", "check"]) else "apply_patch",
                    "target": "Detected via Proactive Analysis",
                    "description": step
                }, ensure_ascii=False))
            
            return {
                "thought": f"시스템 최적화 제안({debate_res.get('final_decision')[:50]}...)을 실행 계획으로 전환했습니다.",
                "next_node": "coder",
                "plan": new_plan,
                "current_step": 0,
                "debate_result": None, 
                "is_recovery_mode": is_recovery,
                "is_guardian_mode": is_guardian,
                "messages": [("ai", f"{mode_title}: {mode_desc}에 따라 코드 개선을 시작합니다.\n\n**목표**: {debate_res.get('final_decision')}")]
            }

        # 3. 선제적 확장(Proactive Expansion) 처리
        ltm_context = ""
        case_context = ""
        if len(internal_input) > 15:
            namespace = os.path.basename(state.get("working_dir", "global"))
            try:
                recalled_items = ltm.recall(internal_input, namespace=namespace)
                ltm_context = "\n".join([f"- {item['content']}" for item in recalled_items])
                
                past_cases = log_search.search_similar_cases(internal_input)
                case_context = "\n".join([f"Case: {c.get('agent')} - {c.get('event')}" for c in past_cases])
            except Exception as e:
                logger.warning(f"Context retrieval failed: {e}")
        
        available_agents = "\n".join([f"- {name}: {registry.get_metadata(name).description} (Tools: {registry.get_metadata(name).tools})" for name in registry.list_agents()])

        # 4. 시스템 프롬프트 구성
        from gortex.utils.prompt_loader import loader
        base_instruction = loader.get_prompt(
            "manager", 
            persona_id=state.get("assigned_persona", "standard"),
            ltm_context=ltm_context, 
            case_context=case_context, 
            persona_context=f"[AVAILABLE AGENTS]\n{available_agents}",
            context_text=internal_input
        )

        # 5. 리소스 기반 모델 결정
        from gortex.core.config import GortexConfig
        budget_limit = GortexConfig().get("daily_budget", 0.5)
        daily_cost = monitor.get_daily_cumulative_cost()
        model_id = LLMFactory.get_model_for_grade("Silver", daily_cost, budget_limit)

        # 6. LLM 호출 및 라우팅
        schema = {
            "type": "OBJECT",
            "properties": {
                "thought": {"type": "STRING"},
                "required_capability": {"type": "STRING"},
                "response_to_user": {"type": "STRING"},
                "ui_mode": {"type": "STRING"}
            },
            "required": ["thought", "required_capability"]
        }

        config = {"temperature": 0.0}
        formatted_messages = [{"role": "system", "content": base_instruction}]
        for m in state["messages"]:
            role = m[0] if isinstance(m, tuple) else "user"
            content = m[1] if isinstance(m, tuple) else (m.content if hasattr(m, 'content') else str(m))
            formatted_messages.append({"role": role, "content": content})

        try:
            response_text = self.backend.generate(model=model_id, messages=formatted_messages, config=config)
            
            # [LOGGING] 분석을 위해 원문 기록
            logger.debug(f"RAW Response from {model_id}: {response_text}")
            
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                logger.error(f"Failed to find JSON in response: {response_text}")
                # 원문에 텍스트만 있는 경우 response_to_user로 간주하고 Planner로 토스
                return {
                    "thought": "LLM이 구조화된 형식을 지키지 않았습니다. 원문을 사용자 응답으로 간주하고 계획 단계로 진행합니다.",
                    "next_node": "planner",
                    "messages": [("ai", response_text)]
                }

            res_data = json.loads(json_match.group(0))
            
            req_cap = res_data.get("required_capability", "").lower()
            candidates = registry.get_agents_by_tool(req_cap) or registry.get_agents_by_role(req_cap)
            
            if candidates:
                agent_eco = state.get("agent_economy", {})
                
                # [INTEGRATION] Skill-based Routing
                # 1. 요구 능력에 따른 관련 스킬 카테고리 추론
                skill_map = {
                    "coding": "Coding", "code": "Coding", "patch": "Coding", "write": "Coding",
                    "design": "Design", "plan": "Design", "architect": "Design",
                    "analyze": "Analysis", "audit": "Analysis", "scan": "Analysis",
                    "research": "Research", "search": "Research"
                }
                # 도구명이나 역할명에 키워드가 포함되어 있는지 확인
                target_skill = "General"
                for key, val in skill_map.items():
                    if key in req_cap:
                        target_skill = val
                        break
                
                # 2. 해당 스킬 점수 우선 정렬 (스킬 점수 70% + 총점 30% 가중치)
                def calculate_score(agent_name):
                    data = agent_eco.get(agent_name.lower(), {})
                    skill_score = data.get("skill_points", {}).get(target_skill, 0)
                    total_score = data.get("points", 0)
                    return (skill_score * 0.7) + (total_score * 0.3)

                candidates.sort(key=calculate_score, reverse=True)
                target_node = candidates[0]
                
                if target_skill != "General":
                    logger.info(f"🎯 Routing based on skill '{target_skill}': Selected {target_node}")
            else:
                target_node = "planner"

            target_grade = state.get("agent_economy", {}).get(target_node, {}).get("level", "Bronze")
            final_assigned_model = LLMFactory.get_model_for_grade(target_grade, daily_cost, budget_limit)

            latency_ms = int((time.time() - start_time) * 1000)
            monitor.record_interaction("manager", model_id, True, len(response_text)//4, latency_ms)

            return {
                "thought": res_data.get("thought"),
                "next_node": target_node,
                "assigned_model": final_assigned_model,
                "agent_energy": max(0, energy - 5),
                "required_capability": req_cap,
                "messages": [("ai", res_data.get("response_to_user"))] if res_data.get("response_to_user") else []
            }
        except Exception as e:
            logger.error(f"Manager failed: {e}")
            # 파싱 에러 등의 경우 Planner로 기본 복구 시도
            return {
                "thought": f"Manager 분석 중 오류({e})가 발생하여 기본 계획 단계로 진행합니다.",
                "next_node": "planner", 
                "messages": [("ai", "⚠️ 분석 중 사소한 오류가 있었으나, 계속 진행합니다.")]
            }

# 레지스트리 등록 및 호환성 래퍼
manager_instance = ManagerAgent()
registry.register("Manager", ManagerAgent, manager_instance.metadata)

def manager_node(state: GortexState) -> Dict[str, Any]:
    return manager_instance(state)