import logging
import json
import time
import re
from typing import Dict, Any, List, Optional
from gortex.core.state import GortexState
from gortex.core.llm.factory import LLMFactory
from gortex.utils.tools import read_file, write_file, execute_shell, list_files, get_file_hash, apply_patch, scan_security_risks
from gortex.utils.healing_memory import SelfHealingMemory

logger = logging.getLogger("GortexCoder")

def coder_node(state: GortexState) -> Dict[str, Any]:
    """
    Gortex 시스템의 개발자(Coder) 노드.
    Planner가 수립한 계획을 한 단계씩 실행하며, 검증(Verification)을 통해 코드를 완성합니다.
    (Ollama/Gemini 하이브리드 지원)
    """
    backend = LLMFactory.get_default_backend()
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
        if "Exit Code: 0" not in tool_output:
            instant_solution = healing_mem.find_solution(tool_output)
            if instant_solution:
                logger.info(f"🩹 Instant healing solution found!")
                state["messages"].append(("system", f"HINT: 과거 해결책 발견. '{instant_solution['action']}'(target: {instant_solution['target']})을 시도하십시오."))
    elif action == "list_files":
        tool_output = list_files(target)
    
    # 3. LLM 호출 준비
    from gortex.utils.prompt_loader import loader
    base_instruction = loader.get_prompt(
        "coder", 
        persona_id=state.get("assigned_persona", "standard"),
        current_step_json=json.dumps(current_step, ensure_ascii=False, indent=2),
        tool_output=(tool_output if tool_output else "(Not executed yet)")
    )
    
    if state.get("active_constraints"):
        constraints_str = "\n".join([f"- {c}" for c in state["active_constraints"]])
        base_instruction += f"\n\n[USER-SPECIFIC EVOLVED RULES]\n{constraints_str}"

    # 백엔드 능력에 따른 설정 분기
    assigned_model = state.get("assigned_model", "gemini-1.5-flash")
    config = {"temperature": 0.0}
    
    # [Hybrid Strategy] Native 기능을 지원하지 않는 경우 프롬프트 보강
    if not backend.supports_structured_output():
        base_instruction += "\n[IMPORTANT: OUTPUT FORMAT]\nYou must respond in the following JSON format ONLY. Do not include any other text outside the JSON block."
        base_instruction += "{\n  \"thought\": \"Your reasoning here\",\n  \"thought_tree\": [{\"id\": \"1\", \"text\": \"...\", \"type\": \"analysis\", \"priority\": 1, \"certainty\": 0.9}],\n  \"simulation\": {\n    \"expected_outcome\": \"...\",\n    \"risk_level\": \"Low|Medium|High\",\n    \"safeguard_action\": \"...\",\n    \"visual_delta\": [{\"target\": \"file.py\", \"change\": \"modified\"}]\n  },\n  \"action\": \"write_file|apply_patch|execute_shell|read_file|list_files|none\",\n  \"action_input\": { ... parameters for the action ... },\n  \"status\": \"success|in_progress|failed\"\n}"
    else:
        # Gemini 등 Native 지원 시 전용 객체 구성 (기존 로직 유지 시도)
        from google.genai import types
        gemini_config = types.GenerateContentConfig(
            system_instruction=base_instruction,
            temperature=0.0,
            response_mime_type="application/json",
            tools=[read_file, write_file, execute_shell, list_files, apply_patch],
            # schema 생략 (GeminiBackend가 처리하거나 여기서 넘김)
        )
        config = gemini_config

    # 메시지 변환 (LLMBackend 표준 포맷)
    formatted_messages = []
    # 시스템 지침을 첫 번째 메시지로 (또는 config에 포함)
    formatted_messages.append({"role": "system", "content": base_instruction})
    for m in state["messages"]:
        role = m[0]
        content = m[1]
        formatted_messages.append({"role": role, "content": content})

    # LLM 호출
    logger.info(f"Coder calling backend with model: {assigned_model}")
    try:
        response_text = backend.generate(model=assigned_model, messages=formatted_messages, config=config)
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        return {
            "messages": [("system", f"ERROR: LLM 호출 실패 - {e}")],
            "next_node": "coder",
            "coder_iteration": current_iteration + 1
        }

    # 4. 응답 파싱 및 실행
    res_data = {}
    function_calls = []

    try:
        # JSON 블록 추출 (Ollama 등 텍스트 섞여 나오는 경우 대비)
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            res_data = json.loads(json_match.group(0))
        else:
            res_data = json.loads(response_text)
            
        coder_thought = res_data.get("thought", "Processing...")
        coder_tree = res_data.get("thought_tree", [])
        status = res_data.get("status", "in_progress")
        
        # Native Function Call이 아닌 경우 action 필드 확인
        if "action" in res_data and res_data["action"] != "none":
            # 가상 Function Call 객체 생성
            fname = res_data["action"]
            fargs = res_data.get("action_input", {})
            function_calls.append(type('obj', (object,), {'name': fname, 'args': fargs}))
            
    except Exception as e:
        logger.warning(f"Failed to parse LLM response: {e}")
        coder_thought = "Response parsing failed."
        coder_tree = []
        status = "failed"

    # [Compatibility] Gemini Backend의 경우 function_calls가 별도로 있을 수 있음
    # (현재 backend.generate는 text만 리턴하므로, 추후 backend 인터페이스 고도화 필요)
    # 일단 텍스트 기반 파싱으로 통일하거나 Gemini 전용 로직 보강

    if function_calls:
        fc = function_calls[0]
        fname = fc.name
        fargs = fc.args
        result_msg = ""
        new_file_cache = state.get("file_cache", {}).copy()

        # [Compliance & Security Check] (기존 로직 유지)
        from gortex.agents.analyst import AnalystAgent
        compliance_res = AnalystAgent().validate_constraints(
            state.get("active_constraints", []),
            {"action": fname, "target": fargs.get("path") or fargs.get("command") or fargs.get("directory"), "args": fargs}
        )
        
        if not compliance_res.get("is_valid", True):
            return {
                "thought": f"정책 위반: {compliance_res.get('reason')}",
                "coder_iteration": current_iteration + 1,
                "messages": [("ai", "❌ 정책 위반으로 차단됨"), ("system", compliance_res.get('reason'))],
                "next_node": "coder"
            }

        if fname == "write_file":
            result_msg = write_file(fargs["path"], fargs["content"])
            new_file_cache[fargs["path"]] = get_file_hash(fargs["path"])
        elif fname == "apply_patch":
            result_msg = apply_patch(fargs["path"], int(fargs["start_line"]), int(fargs["end_line"]), fargs["new_content"])
            new_file_cache[fargs["path"]] = get_file_hash(fargs["path"])
        elif fname == "execute_shell":
            result_msg = execute_shell(fargs["command"])
        elif fname == "read_file":
            result_msg = read_file(fargs["path"])
        elif fname == "list_files":
            result_msg = list_files(fargs.get("directory", "."))
            
        return {
            "thought": coder_thought, "thought_tree": coder_tree,
            "coder_iteration": current_iteration + 1, "file_cache": new_file_cache,
            "messages": [("ai", f"Executed {fname}"), ("tool", result_msg)],
            "next_node": "coder"
        }

    if status == "success":
        # [Recursion Guard] pre-commit이 이미 실행 중이면 다시 호출하지 않음
        import os
        if os.environ.get("GORTEX_PRE_COMMIT_ACTIVE") == "true":
            logger.info("Pre-commit guard active: Skipping recursive check.")
            return {
                "current_step": current_step_idx + 1, "coder_iteration": 0,
                "next_node": "coder", "messages": [("ai", f"✅ Step {current_step_idx+1} 완료 (Guard Active)")]
            }

        # 검증 루프 (기존 로직)
        from gortex.utils.tools import get_changed_files
        changed_files = get_changed_files(state.get("working_dir", "."), state.get("file_cache", {}))
        
        # 쉘 명령어 레벨에서 환경 변수 설정 후 실행
        check_res = execute_shell(f"GORTEX_PRE_COMMIT_ACTIVE=true ./scripts/pre_commit.sh --selective {' '.join(changed_files)}")
        
        if "Ready to commit" in check_res:
            return {
                "current_step": current_step_idx + 1, "coder_iteration": 0,
                "next_node": "coder", "messages": [("ai", f"✅ Step {current_step_idx+1} 완료")]
            }
        else:
            return {
                "thought": "Correction needed.", "coder_iteration": current_iteration + 1,
                "messages": [("ai", "❌ 검증 실패"), ("tool", check_res)],
                "next_node": "coder"
            }
            
    return {
        "thought": coder_thought, "thought_tree": coder_tree,
        "coder_iteration": current_iteration + 1, "next_node": "coder"
    }