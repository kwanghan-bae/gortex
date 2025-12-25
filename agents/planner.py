import logging
import json
import time
import re
from typing import Dict, Any, List
from gortex.core.state import GortexState
from gortex.agents.base import BaseAgent
from gortex.core.registry import AgentMetadata, registry
from gortex.utils.tools import list_files
from gortex.utils.indexer import SynapticIndexer
from gortex.utils.efficiency_monitor import EfficiencyMonitor
from gortex.utils.translator import i18n

logger = logging.getLogger("GortexPlanner")

class PlannerAgent(BaseAgent):
    """
    Gortex 시스템의 설계자(Planner) 에이전트.
    사용자의 목표를 달성하기 위해 원자적 단위의 실행 계획을 수립합니다.
    """
    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="Planner",
            role="Architect",
            description="Builds step-by-step execution plans and analyzes architectural impact.",
            tools=["list_files", "search_index"],
            version="3.0.0"
        )

    def run(self, state: GortexState) -> Dict[str, Any]:
        indexer = SynapticIndexer()
        monitor = EfficiencyMonitor()
        start_time = time.time()
        
        # 1. 인덱스 기반 맥락 정보 추출
        last_msg_obj = state["messages"][-1]
        last_msg = last_msg_obj[1] if isinstance(last_msg_obj, tuple) else last_msg_obj.content
        search_results = indexer.search(last_msg) if last_msg else []
        
        context_info = ""
        if search_results:
            context_info = "\n[Synaptic Index Search Results]\n"
            for res in search_results[:5]:
                context_info += f"- {res['type'].upper()} '{res['name']}' in {res['file']} (Line {res['line']})\n"

        # 2. 현재 환경 파악
        current_files = list_files(state.get("working_dir", "."))
        energy = state.get("agent_energy", 100)
        
        # 3. 시스템 프롬프트 구성
        from gortex.utils.prompt_loader import loader
        base_instruction = loader.get_prompt(
            "planner", 
            persona_id=state.get("assigned_persona", "standard"),
            current_files=current_files, 
            context_info=context_info,
            handoff_instruction=state.get("handoff_instruction", "")
        )
        
        base_instruction += f"\n\n[System Resource State]\n- Current Energy: {energy}/100"
        base_instruction += "\n\nAssign 'priority_score' (1-10) and 'category' (Security, Fix, Feature, Doc, Refactor) to each step. Provide a 'handoff_instruction' for the next agent."

        # 스키마 정의 (Native용)
        schema = {
            "type": "OBJECT",
            "properties": {
                "thought_process": {"type": "STRING"},
                "impact_analysis": {"type": "OBJECT", "properties": {"target": {"type": "STRING"}, "direct": {"type": "ARRAY", "items": {"type": "STRING"}}, "indirect": {"type": "ARRAY", "items": {"type": "STRING"}}, "risk_level": {"type": "STRING"}}},
                "thought_tree": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {"id": {"type": "STRING"}, "text": {"type": "STRING"}, "type": {"type": "STRING"}, "priority": {"type": "INTEGER"}, "certainty": {"type": "NUMBER"}}}},
                "goal": {"type": "STRING"},
                "steps": {
                    "type": "ARRAY", 
                    "items": {
                        "type": "OBJECT", 
                        "properties": {
                            "id": {"type": "INTEGER"}, 
                            "action": {"type": "STRING"}, 
                            "target": {"type": "STRING"}, 
                            "reason": {"type": "STRING"}, 
                            "priority_score": {"type": "INTEGER"}, 
                            "category": {"type": "STRING", "enum": ["Security", "Fix", "Feature", "Doc", "Refactor"]},
                            "is_essential": {"type": "BOOLEAN"}
                        }
                    }
                },
                "handoff_instruction": {"type": "STRING"}
            },
            "required": ["thought_process", "goal", "steps", "handoff_instruction"]
        }

        assigned_model = state.get("assigned_model", "gemini-1.5-flash")
        config = {"temperature": 0.0}
        
        formatted_messages = [{"role": "system", "content": base_instruction}]
        for m in state["messages"]:
            role = m[0] if isinstance(m, tuple) else "user"
            content = m[1] if isinstance(m, tuple) else (m.content if hasattr(m, 'content') else str(m))
            formatted_messages.append({"role": role, "content": content})

        try:
            response_text = self.backend.generate(model=assigned_model, messages=formatted_messages, config=config)
            
            # [LOGGING] 분석을 위해 원문 기록
            logger.debug(f"RAW Response from Planner: {response_text}")
            
            from gortex.utils.tools import safe_json_extract
            plan_data = safe_json_extract(response_text)
            
            if not plan_data:
                # JSON을 못 찾았거나 파싱 실패 시 기본 계획 생성
                logger.warning("Failed to parse JSON in Planner response. Using fallback.")
                plan_data = {
                    "thought_process": "구조화된 계획 생성에 실패하여 복구 모드로 전환합니다.",
                    "goal": "상태 복구",
                    "steps": [{"id": 1, "action": "research", "target": "error", "reason": "Parsing failed", "priority_score": 10, "category": "Fix"}],
                    "handoff_instruction": "계획을 수동으로 재수립하라."
                }
            
            raw_steps = plan_data.get("steps", [])
            final_steps = []
            pruned_count = 0
            
            # [Prediction] 전체 계획의 리소스 소모 예측
            total_predicted_tokens = 0
            total_predicted_ms = 0
            for step in raw_steps:
                # 작업 유형별 에이전트 추측 (단순화: action 이름 활용)
                target_agent = "coder" if step.get("action") in ["write_file", "apply_patch"] else "researcher"
                prediction = monitor.predict_resource_usage(target_agent)
                total_predicted_tokens += prediction["avg_tokens"]
                total_predicted_ms += prediction["avg_latency_ms"]

            # 리소스 임계치 체크 및 경고
            from gortex.core.config import GortexConfig
            budget_limit = GortexConfig().get("daily_budget", 0.5)
            from gortex.utils.token_counter import estimate_cost
            expected_cost = estimate_cost(total_predicted_tokens)
            
            resource_alert = False
            if expected_cost > (budget_limit * 0.2): # 일일 예산의 20% 초과 시
                resource_alert = True
                logger.warning(f"🚨 Resource Alert: Expected cost ${expected_cost:.4f} is high.")

            for step in raw_steps:
                if energy < 30 and step.get("category") == "Doc" and step.get("priority_score", 5) < 7:
                    pruned_count += 1
                    continue
                final_steps.append(step)
            
            # [Intelligent Sorting] 우선순위 점수 내림차순 정렬 (높은 점수가 먼저)
            # 단, id(원래 순서)를 보조 정렬 키로 사용하여 논리적 흐름 유지
            final_steps.sort(key=lambda x: (x.get("priority_score", 5), -x.get("id", 0)), reverse=True)
            
            plan_steps = [json.dumps(step, ensure_ascii=False) for step in final_steps]
            latency_ms = int((time.time() - start_time) * 1000)
            monitor.record_interaction("planner", assigned_model, True, len(response_text)//4, latency_ms)

            msg = i18n.t("task.plan_established", goal=plan_data.get('goal'), steps=len(plan_steps))
            if pruned_count > 0: msg += f" (⚠️ {pruned_count} steps pruned for energy)"
            if resource_alert: msg += f"\n⚠️ **High Resource Usage Predicted**: ${expected_cost:.4f} expected."

            # [INTEGRATION] Update Skill Points on Success (Design category for Architect)
            from gortex.utils.economy import get_economy_manager
            eco_manager = get_economy_manager()
            eco_manager.update_skill_points(
                state, 
                self.metadata.name, 
                category="Design", 
                quality_score=1.1, 
                difficulty=1.2
            )

            return {
                "thought_process": plan_data.get("thought_process"),
                "impact_analysis": plan_data.get("impact_analysis"),
                "thought_tree": plan_data.get("thought_tree"),
                "plan": plan_steps,
                "current_step": 0,
                "next_node": "coder",
                "handoff_instruction": plan_data.get("handoff_instruction", ""),
                "predicted_usage": {
                    "tokens": total_predicted_tokens,
                    "cost": expected_cost,
                    "latency_ms": total_predicted_ms
                },
                "messages": [("ai", msg)],
                "agent_economy": state.get("agent_economy")
            }
        except Exception as e:
            logger.error(f"Planner failed: {e}")
            return {"next_node": "__end__", "messages": [("ai", f"❌ Planning Error: {e}")]}

# 레지스트리 등록 및 호환성 래퍼
planner_instance = PlannerAgent()
registry.register("Planner", PlannerAgent, planner_instance.metadata)

def planner_node(state: GortexState) -> Dict[str, Any]:
    return planner_instance(state)