import logging
import json
import time
import re
import os
from typing import Dict, Any
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

    def spawn_new_agent(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """제안된 명세를 바탕으로 새로운 전문가 에이전트를 영입함."""
        agent_name = proposal["agent_name"]
        file_name = f"agents/auto_spawned_{agent_name.lower()}.py"
        
        prompt = f"""You are the Master Recruiter. 
        Create a high-performance Gortex Agent class based on this blueprint.
        
        [Proposal]:
        {json.dumps(proposal, indent=2, ensure_ascii=False)}
        
        Requirements:
        1. Inherit from 'gortex.agents.base.BaseAgent'.
        2. Implement 'metadata' property with name, role, and required tools.
        3. Implement 'run' method using the 'logic_strategy'.
        4. MUST include 'from gortex.core.registry import registry' and register the instance at the end.
        5. The code must be self-contained and ready to be imported.
        
        Return ONLY valid Python code.
        """
        
        try:
            code = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}])
            code = re.sub(r'```python\n|```', '', code).strip()
            
            # 파일 안전 쓰기
            write_file(file_name, code)
            
            # 동적 로드 시도
            from gortex.core.registry import registry
            success = registry.load_agent_from_file(file_name)
            
            if success:
                logger.info(f"✨ New elite agent '{agent_name}' has joined the team via {file_name}")
                return {"status": "success", "file": file_name, "agent": agent_name}
            else:
                return {"status": "failed", "reason": "Runtime injection failed"}
                
        except Exception as e:
            logger.error(f"Failed to spawn agent: {e}")
            return {"status": "error", "reason": str(e)}

    def generate_regression_test(self, target_file: str, risk_info: str = "") -> Dict[str, Any]:
        """특정 소스 코드에 대한 회귀 테스트를 자동으로 생성함."""
        source_code = read_file(target_file)
        file_name = os.path.basename(target_file)
        test_file = f"tests/test_auto_{file_name}"
        
        prompt = f"""Generate a robust Python unittest for the following code.
        
        [Source File]: {target_file}
        [Risk Info]: {risk_info}
        [Code]:
        {source_code}
        
        Requirements:
        1. Use 'unittest' standard library.
        2. Use 'unittest.mock' to isolate dependencies.
        3. Include Happy Path, Edge Cases (empty input, None, etc.), and Exception handling.
        4. Follow the project's existing test style.
        5. The test file must be runnable with 'python3 -m unittest {test_file}'.
        
        Output ONLY the complete Python code. No conversational text.
        """
        
        try:
            test_code = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}])
            test_code = re.sub(r'```python\n|```', '', test_code).strip()
            
            # 테스트 파일 작성
            write_file(test_file, test_code)
            
            # 즉시 실행 검증
            res = execute_shell(f"python3 -m unittest {test_file}")
            success = "OK" in res
            
            if success:
                logger.info(f"🛡️ Regression test generated and passed: {test_file}")
                return {"status": "success", "file": test_file, "passed": True}
            else:
                logger.warning(f"⚠️ Generated test failed initial run: {res}")
                return {"status": "failed", "file": test_file, "passed": False, "error": res}
                
        except Exception as e:
            logger.error(f"Regression test generation failed: {e}")
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
                
                # [INTEGRATION] Tool Permission Check
                economy_data = state.get("agent_economy", {})
                if not registry.is_tool_permitted(self.metadata.name, fname, economy_data):
                    return {
                        "thought": f"I tried to use {fname} but I don't have enough skill points yet.",
                        "messages": [("ai", f"🚫 Access Denied: {fname} is locked.")],
                        "next_node": "coder",
                        "coder_iteration": current_iteration + 1
                    }

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
                # [INTEGRATION] Update Skill Points on Success
                from gortex.utils.economy import get_economy_manager
                eco_manager = get_economy_manager()
                
                # Coding 분야 스킬 포인트 업데이트 (기본 품질 1.2, 난이도 1.5 가정 - 향후 Analyst가 평가)
                eco_manager.update_skill_points(
                    state, 
                    self.metadata.name, 
                    category="Coding", 
                    quality_score=1.2, 
                    difficulty=1.5
                )
                
                return {
                    "current_step": current_step_idx + 1,
                    "coder_iteration": 0,
                    "next_node": "coder",
                    "messages": [("ai", f"✅ Step {current_step_idx+1} complete")],
                    "agent_economy": state.get("agent_economy") # 업데이트된 경제 정보 전파
                }
            
            return {"thought": coder_thought, "coder_iteration": current_iteration + 1, "next_node": "coder"}
        except Exception as e:
            return {"next_node": "coder", "coder_iteration": current_iteration + 1, "messages": [("system", f"Error: {e}")]}

# 레지스트리 등록 및 호환성 래퍼
coder_instance = CoderAgent()
registry.register("Coder", CoderAgent, coder_instance.metadata)

def coder_node(state: GortexState) -> Dict[str, Any]:
    return coder_instance(state)
