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
    
    # 3. Gemini 호출 (외부 템플릿 로드)
    from gortex.utils.prompt_loader import loader
    base_instruction = loader.get_prompt(
        "coder", 
        current_step_json=json.dumps(current_step, ensure_ascii=False, indent=2),
        tool_output=(tool_output if tool_output else "(Not executed yet)")
    )
    
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
                        },
                        "expected_graph_delta": {
                            "type": "OBJECT",
                            "properties": {
                                "added_nodes": {"type": "ARRAY", "items": {"type": "STRING"}},
                                "modified_nodes": {"type": "ARRAY", "items": {"type": "STRING"}},
                                "deleted_nodes": {"type": "ARRAY", "items": {"type": "STRING"}}
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
    
    # [Dynamic Model] Manager가 할당한 모델 사용
    assigned_model = state.get("assigned_model", "gemini-1.5-flash")
    logger.info(f"Coder using model: {assigned_model}")
    
    response = auth.generate(model_id=assigned_model, contents=state["messages"], config=config)
    
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

        # [Compliance Check] 도구 실행 전 실시간 제약 조건 검증
        from gortex.agents.analyst import AnalystAgent
        compliance_res = AnalystAgent().validate_constraints(
            state.get("active_constraints", []),
            {"action": fname, "target": fargs.get("path") or fargs.get("command") or fargs.get("directory"), "args": fargs}
        )
        
        if not compliance_res.get("is_valid", True):
            logger.warning(f"🛡️ Policy violation detected: {compliance_res.get('reason')}")
            return {
                "thought": f"정책 위반 감지: {compliance_res.get('reason')}",
                "thought_tree": coder_tree,
                "coder_iteration": current_iteration + 1,
                "messages": [
                    ("ai", f"❌ 시스템 정책 위반으로 실행이 차단되었습니다."),
                    ("system", f"위반 규칙: {', '.join(compliance_res.get('violated_rules', []))}\n사유: {compliance_res.get('reason')}\n권고: {compliance_res.get('remedy')}")
                ],
                "next_node": "coder"
            }

        # [SECURITY SCAN] 도구 호출 전 실시간 보안 검사 (기존 로직)
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
        # [Autonomous Pre-Commit] 성공 보고 전 자율 검증 수행
        logger.info("🧪 Running autonomous pre-commit check...")
        check_res = execute_shell("./scripts/pre_commit.sh")
        
        if "Ready to commit" in check_res:
            logger.info("✅ Autonomous check passed.")
            return {
                "thought": coder_thought, "thought_tree": coder_tree,
                "current_step": current_step_idx + 1, "coder_iteration": 0,
                "next_node": "coder", "messages": [("ai", f"Step {current_step_idx+1} 완료 및 검증 통과.")]
            }
        else:
            logger.warning("❌ Autonomous check failed. Triggering self-correction...")
            # 실패 로그와 함께 다시 Coder에게 기회 부여 (또는 Analyst로 라우팅)
            return {
                "thought": f"Pre-commit failed after success attempt. Needs correction. Log: {check_res[:200]}",
                "thought_tree": coder_tree,
                "coder_iteration": current_iteration + 1,
                "messages": [
                    ("ai", "❌ 자율 검증 실패로 인해 자가 수정을 시도합니다."),
                    ("tool", check_res)
                ],
                "next_node": "coder"
            }
            
    elif status == "failed":
        # [Reflective Debugging] 실패 원인 분석 및 규칙 생성
        from gortex.agents.analyst import AnalystAgent
        analyst = AnalystAgent()
        rule_data = analyst.generate_anti_failure_rule(tool_output, coder_thought)
        
        msg = "⚠️ 반복 실패로 분석을 수행했습니다."
        if rule_data:
            msg += f"\n🛡️ 새로운 방어 규칙이 생성되었습니다: {rule_data['instruction']}"
            
        return {
            "thought": f"Failed: {coder_thought}. Reflection complete.", "thought_tree": coder_tree,
            "next_node": "analyst", "messages": [("ai", msg)]
        }
    else:
        return {
            "thought": coder_thought, "thought_tree": coder_tree,
            "coder_iteration": current_iteration + 1, "next_node": "coder"
        }
