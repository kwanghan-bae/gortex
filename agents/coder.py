import logging
import json
import time
import re
from typing import Dict, Any, List, Optional
from gortex.core.state import GortexState
from gortex.agents.base import BaseAgent
from gortex.core.registry import AgentMetadata, registry
from gortex.utils.tools import read_file, write_file, execute_shell, list_files, get_file_hash, apply_patch
from gortex.utils.healing_memory import SelfHealingMemory
from gortex.utils.efficiency_monitor import EfficiencyMonitor

logger = logging.getLogger("GortexCoder")

class CoderAgent(BaseAgent):
    """
    Gortex 시스템의 개발자(Coder) 에이전트.
    Planner가 수립한 계획을 한 단계씩 실행하며, 검증을 통해 코드를 완성합니다.
    """
    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="Coder",
            role="Developer",
            description="Implements code changes, runs tests, and fixes bugs autonomously.",
            tools=["write_file", "apply_patch", "execute_shell", "read_file", "list_files"],
            version="3.0.0"
        )

    def generate_new_agent(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        제공된 명세(Analyst 제안)를 바탕으로 새로운 에이전트 클래스 코드를 생성하고 레지스트리에 등록함.
        """
        agent_name = spec["agent_name"]
        file_name = f"agents/auto_{agent_name.lower()}.py"
        
        prompt = f"""Create a new Gortex Agent class based on this specification.
        
        [Spec]:
        {json.dumps(spec, indent=2)}
        
        Requirements:
        1. Inherit from 'gortex.agents.base.BaseAgent'.
        2. Implement 'metadata' property using 'AgentMetadata'.
        3. Implement 'run' method with provided 'logic_strategy'.
        4. Register the instance at the end of the file using 'gortex.core.registry.registry.register'.
        
        Output ONLY the complete Python code. No conversational text.
        """
        
        try:
            code = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}])
            code = re.sub(r'```python\n|```', '', code).strip()
            
            # 파일 작성
            write_file(file_name, code)
            
            # 동적 로드 및 레지스트리 등록 시도
            from gortex.core.registry import registry
            success = registry.load_agent_from_file(file_name)
            
            if success:
                logger.info(f"✨ New agent '{agent_name}' spawned and registered via {file_name}")
                return {"status": "success", "file": file_name, "agent": agent_name}
            else:
                return {"status": "failed", "reason": "Dynamic loading failed after file creation"}
                
        except Exception as e:
            logger.error(f"Agent generation failed: {e}")
            return {"status": "error", "reason": str(e)}

    def run(self, state: GortexState) -> Dict[str, Any]:
        healing_mem = SelfHealingMemory()
        monitor = EfficiencyMonitor()
        start_time = time.time()
        
        current_iteration = state.get("coder_iteration", 0)
        if current_iteration >= 30:
            return {"messages": [("ai", "❌ Coder limit reached.")], "next_node": "__end__"}
        
        plan = state.get("plan", [])
        current_step_idx = state.get("current_step", 0)
        if current_step_idx >= len(plan):
            return {"messages": [("ai", "✅ All steps completed.")], "next_node": "analyst"}
        
        current_step = json.loads(plan[current_step_idx])
        action = current_step.get("action")
        target = current_step.get("target")
        
        tool_output = ""
        if action == "read_file": tool_output = read_file(target)
        elif action == "execute_shell": tool_output = execute_shell(target)
        elif action == "list_files": tool_output = list_files(target)
        
        from gortex.utils.prompt_loader import loader
        base_instruction = loader.get_prompt(
            "coder", 
            persona_id=state.get("assigned_persona", "standard"),
            current_step_json=json.dumps(current_step, ensure_ascii=False, indent=2),
            tool_output=tool_output or "(N/A)",
            handoff_instruction=state.get("handoff_instruction", "")
        )

        assigned_model = state.get("assigned_model", "gemini-1.5-flash")
        formatted_messages = [{"role": "system", "content": base_instruction}]
        for m in state["messages"]:
            role = m[0] if isinstance(m, tuple) else "user"
            content = m[1] if isinstance(m, tuple) else (m.content if hasattr(m, 'content') else str(m))
            formatted_messages.append({"role": role, "content": content})

        try:
            response_text = self.backend.generate(model=assigned_model, messages=formatted_messages)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            res_data = json.loads(json_match.group(0)) if json_match else json.loads(response_text)
            
            coder_thought = res_data.get("thought", "Working...")
            status = res_data.get("status", "in_progress")
            
            if "action" in res_data and res_data["action"] != "none":
                fname = res_data["action"]
                fargs = res_data.get("action_input", {})
                result_msg = ""
                new_file_cache = state.get("file_cache", {}).copy()

                if fname == "write_file":
                    result_msg = write_file(fargs["path"], fargs["content"])
                    new_file_cache[fargs["path"]] = get_file_hash(fargs["path"])
                elif fname == "apply_patch":
                    result_msg = apply_patch(fargs["path"], int(fargs["start_line"]), int(fargs["end_line"]), fargs["new_content"])
                    new_file_cache[fargs["path"]] = get_file_hash(fargs["path"])
                elif fname == "execute_shell":
                    result_msg = execute_shell(fargs["command"])
                
                return {
                    "thought": coder_thought,
                    "coder_iteration": current_iteration + 1,
                    "file_cache": new_file_cache,
                    "messages": [("ai", f"Executed {fname}"), ("tool", result_msg)],
                    "next_node": "coder"
                }

            if status == "success":
                return {
                    "current_step": current_step_idx + 1,
                    "coder_iteration": 0,
                    "next_node": "coder",
                    "messages": [("ai", f"✅ Step {current_step_idx+1} complete")]
                }
            
            return {"thought": coder_thought, "coder_iteration": current_iteration + 1, "next_node": "coder"}
        except Exception as e:
            return {"next_node": "coder", "coder_iteration": current_iteration + 1, "messages": [("system", f"Error: {e}")]}

# 레지스트리 등록 및 호환성 래퍼
coder_instance = CoderAgent()
registry.register("Coder", CoderAgent, coder_instance.metadata)

def coder_node(state: GortexState) -> Dict[str, Any]:
    return coder_instance(state)
