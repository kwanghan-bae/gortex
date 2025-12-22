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
        base_instruction += "\n\nAssign 'priority' (1-10) and 'is_essential' (true/false) to each step. Provide a 'handoff_instruction' for the next agent."

        # 스키마 정의 (Native용)
        schema = {
            "type": "OBJECT",
            "properties": {
                "thought_process": {"type": "STRING"},
                "impact_analysis": {"type": "OBJECT", "properties": {"target": {"type": "STRING"}, "direct": {"type": "ARRAY", "items": {"type": "STRING"}}, "indirect": {"type": "ARRAY", "items": {"type": "STRING"}}, "risk_level": {"type": "STRING"}}},
                "thought_tree": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {"id": {"type": "STRING"}, "text": {"type": "STRING"}, "type": {"type": "STRING"}, "priority": {"type": "INTEGER"}, "certainty": {"type": "NUMBER"}}}},
                "goal": {"type": "STRING"},
                "steps": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {"id": {"type": "INTEGER"}, "action": {"type": "STRING"}, "target": {"type": "STRING"}, "reason": {"type": "STRING"}, "priority": {"type": "INTEGER"}, "is_essential": {"type": "BOOLEAN"}}}},
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
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            plan_data = json.loads(json_match.group(0)) if json_match else json.loads(response_text)
            
            raw_steps = plan_data.get("steps", [])
            final_steps = []
            pruned_count = 0
            for step in raw_steps:
                if energy < 30 and not step.get("is_essential", True) and step.get("priority", 5) < 8:
                    pruned_count += 1
                    continue
                final_steps.append(step)
            
            plan_steps = [json.dumps(step, ensure_ascii=False) for step in final_steps]
            latency_ms = int((time.time() - start_time) * 1000)
            monitor.record_interaction("planner", assigned_model, True, len(response_text)//4, latency_ms)

            msg = i18n.t("task.plan_established", goal=plan_data.get('goal'), steps=len(plan_steps))
            if pruned_count > 0: msg += f" (⚠️ {pruned_count} steps pruned for energy)"

            return {
                "thought_process": plan_data.get("thought_process"),
                "impact_analysis": plan_data.get("impact_analysis"),
                "thought_tree": plan_data.get("thought_tree"),
                "plan": plan_steps,
                "current_step": 0,
                "next_node": "coder",
                "handoff_instruction": plan_data.get("handoff_instruction", ""),
                "messages": [("ai", msg)]
            }
        except Exception as e:
            logger.error(f"Planner failed: {e}")
            return {"next_node": "__end__", "messages": [("ai", f"❌ Planning Error: {e}")]}

# 레지스트리 등록 및 호환성 래퍼
planner_instance = PlannerAgent()
registry.register("Planner", PlannerAgent, planner_instance.metadata)

def planner_node(state: GortexState) -> Dict[str, Any]:
    return planner_instance(state)