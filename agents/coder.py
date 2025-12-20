import logging
import json
import time
from typing import Dict, Any, List
from google.genai import types
from gortex.core.auth import GortexAuth
from gortex.core.state import GortexState
from gortex.utils.tools import read_file, write_file, execute_shell, list_files, get_file_hash

logger = logging.getLogger("GortexCoder")

def coder_node(state: GortexState) -> Dict[str, Any]:

    """
    Gortex 시스템의 개발자(Coder) 노드.
    Planner가 수립한 계획을 한 단계씩 실행하며, 검증(Verification)을 통해 코드를 완성합니다.
    """
    auth = GortexAuth()
    
    # 0. 반복 횟수 체크 (무한 루프 방지)
    current_iteration = state.get("coder_iteration", 0)
    if current_iteration >= 30: # SPEC: MAX_CODER_ITERATIONS = 30
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
    
    # JSON 문자열로 저장된 step 파싱
    current_step_json = plan[current_step_idx]
    try:
        current_step = json.loads(current_step_json)
    except json.JSONDecodeError:
        logger.error(f"Invalid plan step JSON: {current_step_json}")
        return {"next_node": "__end__"}
        
    logger.info(f"Executing Step {current_step_idx + 1}: {current_step['action']} -> {current_step['target']}")
    
    # 2. 도구 실행 (Action Execution)
    tool_output = ""
    action = current_step["action"]
    target = current_step["target"]
    
    if action == "read_file":
        tool_output = read_file(target)
    elif action == "write_file":
        # write_file의 경우 내용은 LLM이 생성해야 함.
        # 따라서 여기서는 바로 실행하지 않고, LLM에게 "이 파일을 작성해줘"라고 요청한 뒤
        # Function Calling을 통해 실제 write_file을 호출하게 유도하거나,
        # Planner가 구체적인 내용을 주지 않았다면 Coder가 내용을 생성해야 함.
        pass # 아래 LLM 호출 단계에서 처리
    elif action == "execute_shell":
        tool_output = execute_shell(target)
    elif action == "list_files":
        tool_output = list_files(target)
    
    # 3. Gemini 호출 (Code Generation & Verification Analysis)
    # 현재 단계에 필요한 코드를 작성하거나, 실행 결과를 분석하여 다음 행동 결정
    
    base_instruction = f"""너는 Gortex v1.0의 수석 개발자(Coder)다.
현재 Planner가 수립한 계획 중 다음 단계를 실행해야 한다.

[Standard Error Response Manual]
- ModuleNotFoundError: 
  1. 즉시 `execute_shell`로 `pip install <module>`을 실행하라. (시스템이 `requirements.txt`를 자동 업데이트할 것이다.)
  2. 설치 완료 후, `requirements.txt`가 업데이트 되었는지 `read_file`로 확인하고 코드를 재검증하라.
- IndentationError/SyntaxError:
  1. `read_file`로 소스 전체를 다시 읽어 코드의 계층 구조를 재파악하라.
  2. 누락된 괄호나 `:`를 찾고, 공백 4칸 기준 들여쓰기를 전수 점검하라.
  3. 수정 전, 기존의 `try-except` 블록이나 `with` 문 내부의 정렬 상태를 다시 확인하라.
- FileNotFoundError: `list_files`로 파일 경로를 재확인하고, 상대 경로가 정확한지 검토하라.
- PermissionError: `execute_shell`로 `chmod` 명령어를 사용하여 권한을 확보하라.


[Current Step]
{json.dumps(current_step, ensure_ascii=False, indent=2)}


[Tool Output / Context]
{tool_output if tool_output else "(Not executed yet)"}

[Your Mission]
1. 위 단계가 'write_file'이라면, 파일에 들어갈 코드를 작성하여 도구를 호출하라.
2. 위 단계가 'execute_shell'이고 실행 결과(Tool Output)에 오류(Exit Code != 0)가 있다면, **STDOUT과 STDERR를 정밀 분석하라.** 
   - 문법 에러라면 오타나 누락된 괄호를 찾아 수정하라.
   - 라이브러리 누락 에러라면 `pip install` 단계를 스스로 계획하여 실행하라.
   - 권한 문제라면 `chmod` 등을 시도하라.
3. 성공적으로 수행되었다면 'status': 'success'를 반환하여 다음 단계로 넘어가라.


[Available Tools]
- read_file(path)
- write_file(path, content)
- execute_shell(command)
- list_files(path)

[Output Schema (Strict JSON)]
{{
  "thought": "생각의 과정",
  "tool_call": {{ "name": "tool_name", "args": {{ ... }} }} OR null,
  "status": "success" | "in_progress" | "failed"
}}
"""
    
    # 진화된 제약 조건 주입
    if state.get("active_constraints"):
        constraints_str = "\n".join([f"- {c}" for c in state["active_constraints"]])
        base_instruction += f"\n\n[USER-SPECIFIC EVOLVED RULES]\n{constraints_str}"

    config = types.GenerateContentConfig(
        system_instruction=base_instruction,
        temperature=0.0,
        response_mime_type="application/json",
        tools=[read_file, write_file, execute_shell, list_files] # Function Calling 활성화
    )
    
    response = auth.generate(
        model_id="gemini-3-flash-preview",
        contents=state["messages"], # 대화 히스토리 전달
        config=config
    )
    
    # Function Calling 처리 로직
    # google-genai 라이브러리는 function_calls 속성을 제공함
    function_calls = []
    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.function_call:
                function_calls.append(part.function_call)

    # 도구 호출이 있다면 실행
    if function_calls:
        # 실제 도구 실행은 LangGraph나 별도 로직에서 처리해야 하나, 
        # 여기서는 Coder 노드 안에서 직접 실행하고 결과를 반영하는 방식으로 구현 (단순화)
        # 하지만 원래 LangGraph 패턴은 ToolNode를 별도로 두는 것임.
        # 현재 구조상 Coder가 직접 도구를 실행하고 결과를 확인하는 루프를 돔.
        
        fc = function_calls[0] # 하나만 처리
        fname = fc.name
        fargs = fc.args
        
        logger.info(f"Coder invoking tool: {fname}")
        
        # 텍스트 응답에서 생각 추출 시도 (JSON 파싱)
        coder_thought = ""
        try:
            res_data = json.loads(response.text)
            coder_thought = res_data.get("thought", "")
        except:
            pass

        result_msg = ""
        new_file_cache = state.get("file_cache", {}).copy()

        if fname == "write_file":
            result_msg = write_file(fargs["path"], fargs["content"])
            # 쓰기 후 해시 업데이트
            new_file_cache[fargs["path"]] = get_file_hash(fargs["path"])
        elif fname == "read_file":
            path = fargs["path"]
            current_hash = get_file_hash(path)
            cached_hash = new_file_cache.get(path)
            
            if cached_hash == current_hash and current_hash != "":
                result_msg = f"(Cache Hit) File content is unchanged. Use your memory."
                logger.info(f"Cache hit for {path}")
            else:
                result_msg = read_file(path)
                new_file_cache[path] = current_hash
        elif fname == "execute_shell":
            result_msg = execute_shell(fargs["command"])
        elif fname == "list_files":
            result_msg = list_files(fargs.get("directory", "."))
            
        return {
            "thought": coder_thought,
            "coder_iteration": current_iteration + 1,
            "file_cache": new_file_cache,
            # 도구 실행 결과를 메시지에 추가하여 다음 턴에 문맥으로 사용
            "messages": [
                ("ai", f"Executed {fname}"),
                ("tool", result_msg) 
            ],
            "next_node": "coder" # 자신을 다시 호출하여 결과 검증
        }

    
    # 도구 호출 없이 텍스트 응답만 온 경우 (JSON 파싱 시도)
    try:
        res_text = response.text
        res_data = json.loads(res_text)
        coder_thought = res_data.get("thought", "")
        
        if res_data.get("status") == "success":
            # 현재 단계 완료 -> 다음 단계로 이동
            return {
                "thought": coder_thought,
                "current_step": current_step_idx + 1,
                "coder_iteration": 0, # 단계가 바뀌면 반복 횟수 초기화
                "next_node": "coder", # 다음 단계 실행을 위해 다시 Coder 호출
                "file_cache": state.get("file_cache", {}),
                "messages": [("ai", f"Step {current_step_idx+1} 완료. 다음 단계로 이동.")]
            }
        else:
            # 아직 진행 중이거나 실패
            return {
                "thought": coder_thought,
                "coder_iteration": current_iteration + 1,
                "file_cache": state.get("file_cache", {}),
                "next_node": "coder"
            }
            
    except Exception:
        # JSON 파싱 실패 시 그냥 진행
        return {
            "coder_iteration": current_iteration + 1,
            "file_cache": state.get("file_cache", {}),
            "next_node": "coder"
        }


