import logging
import json
import os
import time
import re
from typing import Dict, List, Any, Optional
from gortex.core.state import GortexState
from gortex.core.llm.factory import LLMFactory
from gortex.core.evolutionary_memory import EvolutionaryMemory
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
        raw_input = last_msg_obj[1] if isinstance(last_msg_obj, tuple) else last_msg_obj.content
        lang_info = translator.detect_and_translate(raw_input)
        internal_input = lang_info.get("translated_text", raw_input) if not lang_info.get("is_korean") else raw_input

        energy = state.get("agent_energy", 100)
        roadmap = state.get("evolution_roadmap", [])

        # 2. 선제적 확장(Proactive Expansion) 처리
        # TrendScout 등으로부터 에이전트 확장 제안이 온 경우
        agent_proposals = state.get("agent_proposals", [])
        if agent_proposals:
            logger.info(f"⚡ Proactive expansion proposal detected: {agent_proposals[0]['agent_name']}")
            # Analyst에게 넘겨 타당성 검토(identify_capability_gap과 유사한 흐름) 후 Coder에게 제조 지시
            return {
                "thought": f"TrendScout의 신규 에이전트 '{agent_proposals[0]['agent_name']}' 영입 제안을 분석합니다.",
                "next_node": "analyst",
                "required_capability": "capability_gap_analysis",
                "handoff_instruction": f"다음 에이전트 제안의 타당성을 검토하라: {json.dumps(agent_proposals[0], ensure_ascii=False)}",
                "messages": [("ai", f"🚀 **시스템 확장 감지**: '{agent_proposals[0]['agent_name']}' 전문가 영입을 위한 타당성 검토를 시작합니다.")]
            }

        # 3. 맥락 정보 수집
        namespace = os.path.basename(state.get("working_dir", "global"))
        recalled_items = ltm.recall(internal_input, namespace=namespace)
        ltm_context = "\n".join([f"- {item['content']}" for item in recalled_items])
        
        past_cases = log_search.search_similar_cases(internal_input)
        case_context = "\n".join([f"Case: {c.get('agent')} - {c.get('event')}" for c in past_cases])
        
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
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            res_data = json.loads(json_match.group(0)) if json_match else json.loads(response_text)
            
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
            return {"next_node": "__end__", "messages": [("ai", f"❌ 분석 오류: {e}")]}

# 레지스트리 등록 및 호환성 래퍼
manager_instance = ManagerAgent()
registry.register("Manager", ManagerAgent, manager_instance.metadata)

def manager_node(state: GortexState) -> Dict[str, Any]:
    return manager_instance(state)