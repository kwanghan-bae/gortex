import logging
import json
import time
from typing import Dict, Any, List
from google.genai import types
from gortex.core.auth import GortexAuth
from gortex.core.state import GortexState
from gortex.utils.tools import read_file, write_file, execute_shell, list_files, get_file_hash, apply_patch, scan_security_risks
from gortex.utils.healing_memory import SelfHealingMemory

logger = logging.getLogger("GortexCoder")

def coder_node(state: GortexState) -> Dict[str, Any]:
    """
    Gortex 시스템의 개발자(Coder) 노드.
    Planner가 수립한 계획을 한 단계씩 실행하며, 검증(Verification)을 통해 코드를 완성합니다.
    """
    auth = GortexAuth()
    healing_mem = SelfHealingMemory()
    
    # 0. 반복 횟수 체크
    current_iteration = state.get("coder_iteration", 0)
    if current_iteration >= 30:
        logger.warning("Coder iteration limit reached.")
        return {
            "messages": [("ai", "❌ 안전을 위해 Coder 루프를 30회에서 중단합니다.")],
            "next_node": "__end__"
        }
    
    # 1. 현재 실행할 단계 가져오기
    plan = state.get("plan", [])
    current_step_idx = state.get("current_step", 0)
    
    if current_step_idx >= len(plan):
        return {
            "messages": [("ai", "✅ 모든 계획된 작업을 완료했습니다.")],
            "next_node": "__end__"
        }
    
    current_step_json = plan[current_step_idx]
    try:
        current_step = json.loads(current_step_json)
    except:
        current_step = {"action": "unknown", "target": "unknown"}
        
    logger.info(f"Executing Step {current_step_idx + 1}: {current_step['action']} -> {current_step['target']}")
    
    # 2. 도구 실행
    tool_output = ""
    action = current_step["action"]
    target = current_step["target"]
    
    if action == "read_file":
        tool_output = read_file(target)
    elif action in ["write_file", "apply_patch"]:
        pass # LLM에서 처리
    elif action == "execute_shell":
        tool_output = execute_shell(target)
        # [SELF-HEALING] 에러 발생 시 즉각적인 해결책 검색
        if "Exit Code: 0" not in tool_output:
            instant_solution = healing_mem.find_solution(tool_output)
            if instant_solution:
                logger.info(f"🩹 Instant healing solution found!")
                state["messages"].append(("system", f"HINT: 과거 해결책 발견. '{instant_solution['action']}'(target: {instant_solution['target']})을 시도하십시오."))
    elif action == "list_files":
        tool_output = list_files(target)
    
    # 3. Gemini 호출
    # f-string 내의 중괄호 이스케이프 주의 ({{, }})
    base_instruction = f"""너는 Gortex v1.0의 수석 개발자(Coder)다.
현재 Planner가 수립한 계획 중 다음 단계를 실행해야 한다.

[Self-Healing]
- 시스템 힌트(HINT)로 과거 해결책이 제공되면, 이를 최우선으로 적용하라.

[Precision Editing Rules]
- 파일 전체를 바꾸기보다 특정 부분만 수정하는 것이 효율적이라면 `apply_patch` 도구를 사용하라.

[Mental Sandbox Rules]
도구를 호출하기 전, 반드시 다음 사항을 미리 '시뮬레이션'하라:
1. 예상 결과 및 위험 분석
2. 안전 가드: 위험 시 'failed' 상태와 함께 대안 제시

[Standard Error Response Manual]
- ModuleNotFoundError: 즉시 `execute_shell`로 `pip install <module>`을 실행하라.
- IndentationError/SyntaxError: `read_file`로 다시 읽어 들여쓰기를 점검하라.

[Current Step]
{json.dumps(current_step, ensure_ascii=False, indent=2)}

[Tool Output / Context]
{tool_output if tool_output else "(Not executed yet)"}

[Your Mission]
1. 위 단계가 'write_file' 또는 'apply_patch'라면, 필요한 코드를 작성하여 도구를 호출하라. **[Reflective Validation]**: 수정 직후에는 반드시 `execute_shell`로 관련 테스트를 실행하여 자가 검증하라.
2. 실행 결과에 오류가 있다면 정밀 분석하여 수정하라. 반복 실패 시 'failed'를 반환하라.
3. 성공 시 'status': 'success'를 반환하라.

[Available Tools]
- read_file(path)
- write_file(path, content)
- apply_patch(path, start_line, end_line, new_content)
- execute_shell(command)
- list_files(path)

[Output Schema (Strict JSON)]
{{{{
  "thought": "생각의 과정",
  "thought_tree": [ {{{{ "id": "1", "text": "...", "type": "analysis", "priority": 3, "certainty": 0.9 }}}} ],
  "simulation": {{{{ 
      "expected_outcome": "...", 
      "risk_level": "Low/Medium/High", 
      "safeguard_action": "...",
      "visual_delta": []
  }}}},
  "status": "success" | "in_progress" | "failed"
}}}} """
    
    if state.get("active_constraints"):
        constraints_str = "\n".join([f"- {c}" for c in state["active_constraints"]])
        base_instruction += f"\n\n[USER-SPECIFIC EVOLVED RULES]\n{constraints_str}"

    config = types.GenerateContentConfig(
        system_instruction=base_instruction,
        temperature=0.0,
        response_mime_type="application/json",
        tools=[read_file, write_file, execute_shell, list_files, apply_patch],
        response_schema={
            "type": "OBJECT",
            "properties": {
                "thought": {"type": "STRING"},
                "thought_tree": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "id": {"type": "STRING"},
                            "parent_id": {"type": "STRING", "nullable": True},
                            "text": {"type": "STRING"},
                            "type": {"type": "STRING", "enum": ["analysis", "action", "verification", "simulation"]},
                            "priority": {"type": "INTEGER"},
                            "certainty": {"type": "NUMBER"}
                        },
                        "required": ["id", "text", "type", "priority", "certainty"]
                    }
                },
                "simulation": {
                    "type": "OBJECT",
                    "properties": {
                        "expected_outcome": {"type": "STRING"},
                        "risk_level": {"type": "STRING", "enum": ["Low", "Medium", "High"]},
                        "safeguard_action": {"type": "STRING"},
                        "visual_delta": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "target": {"type": "STRING"},
                                    "change": {"type": "STRING", "enum": ["added", "modified", "deleted"]}
                                },
                                "required": ["target", "change"]
                            }
                        }
                    },
                    "required": ["expected_outcome", "risk_level", "safeguard_action", "visual_delta"]
                },
                "status": {"type": "STRING", "enum": ["success", "in_progress", "failed"]}
            },
            "required": ["thought", "thought_tree", "simulation", "status"]
        }
    )
    
    response = auth.generate(model_id="gemini-3-flash-preview", contents=state["messages"], config=config)
    
    function_calls = []
    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.function_call:
                function_calls.append(part.function_call)

    try:
        res_data = response.parsed if hasattr(response, 'parsed') else json.loads(response.text)
        coder_thought = res_data.get("thought", "")
        coder_tree = res_data.get("thought_tree", [])
        status = res_data.get("status", "in_progress")
    except:
        coder_thought = "Processing..."
        coder_tree = []
        status = "in_progress"

    if function_calls:
        fc = function_calls[0]
        fname = fc.name
        fargs = fc.args
        result_msg = ""
        new_file_cache = state.get("file_cache", {}).copy()

        # [SECURITY SCAN] 도구 호출 전 실시간 보안 검사
        if fname in ["write_file", "apply_patch"]:
            code_to_check = fargs.get("content") or fargs.get("new_content", "")
            risks = scan_security_risks(code_to_check)
            if risks:
                logger.warning(f"🚨 Security risks detected!")
                return {
                    "thought": f"보안 취약점 감지: {risks[0]['type']}",
                    "thought_tree": coder_tree,
                    "coder_iteration": current_iteration + 1,
                    "messages": [
                        ("ai", f"❌ 보안 취약점({risks[0]['type']}) 감지로 실행이 차단되었습니다."),
                        ("system", "보안 가이드라인을 준수하여 다시 작성하십시오.")
                    ],
                    "next_node": "coder"
                }

        if fname == "write_file":
            result_msg = write_file(fargs["path"], fargs["content"])
            new_file_cache[fargs["path"]] = get_file_hash(fargs["path"])
        elif fname == "apply_patch":
            result_msg = apply_patch(fargs["path"], int(fargs["start_line"]), int(fargs["end_line"]), fargs["new_content"])
            new_file_cache[fargs["path"]] = get_file_hash(fargs["path"])
        elif fname == "read_file":
            path = fargs["path"]
            current_hash = get_file_hash(path)
            if new_file_cache.get(path) == current_hash and current_hash != "":
                result_msg = "(Cache Hit) Content unchanged."
            else:
                result_msg = read_file(path)
                new_file_cache[path] = current_hash
        elif fname == "execute_shell":
            result_msg = execute_shell(fargs["command"])
            # 성공 시 학습
            if "Exit Code: 0" in result_msg and "pip install" in fargs["command"]:
                healing_mem.learn("ModuleNotFoundError", {"action": "execute_shell", "target": fargs["command"]})
        elif fname == "list_files":
            result_msg = list_files(fargs.get("directory", "."))
            
        return {
            "thought": coder_thought, "thought_tree": coder_tree,
            "coder_iteration": current_iteration + 1, "file_cache": new_file_cache,
            "messages": [("ai", f"Executed {fname}"), ("tool", result_msg)],
            "next_node": "coder"
        }

    if status == "success":
        return {
            "thought": coder_thought, "thought_tree": coder_tree,
            "current_step": current_step_idx + 1, "coder_iteration": 0,
            "next_node": "coder", "messages": [("ai", f"Step {current_step_idx+1} 완료.")]
        }
    elif status == "failed":
        return {
            "thought": f"Failed: {coder_thought}", "thought_tree": coder_tree,
            "next_node": "analyst", "messages": [("ai", "⚠️ 반복 실패로 분석을 요청합니다.")]
        }
    else:
        return {
            "thought": coder_thought, "thought_tree": coder_tree,
            "coder_iteration": current_iteration + 1, "next_node": "coder"
        }
