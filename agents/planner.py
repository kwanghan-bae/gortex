import logging
import json
from typing import Dict, Any, List
from google.genai import types
from gortex.core.auth import GortexAuth
from gortex.core.state import GortexState
from gortex.utils.tools import list_files

logger = logging.getLogger("GortexPlanner")

def planner_node(state: GortexState) -> Dict[str, Any]:
    """
    Gortex 시스템의 설계자(Planner) 노드.
    사용자의 목표를 달성하기 위해 원자적 단위(Atomic Unit)의 실행 계획을 수립합니다.
    """
    auth = GortexAuth()
    
    # 1. 현재 환경 파악
    current_files = list_files(state.get("working_dir", "."))
    
    # 2. 시스템 프롬프트 구성
    base_instruction = f"""너는 Gortex v1.0 시스템의 수석 아키텍트(Planner)다.
현재 작업 디렉토리의 파일 구조를 분석하고, 사용자의 목표를 달성하기 위한 구체적이고 검증 가능한 단계(Step)들을 계획하라.

[Current File Structure]
{current_files}

[Planning Rules]
1. 작업을 '원자적 단위(Atomic Unit)'로 쪼개라. (예: "로그인 구현" -> "파일 읽기" -> "코드 작성" -> "테스트 실행")
2. 각 단계는 `coder` 에이전트가 수행할 수 있는 구체적인 행동이어야 한다.
3. 사용 가능한 도구(Action):
   - read_file: 파일 내용 확인 (수정 전 필수)
   - write_file: 파일 생성 또는 수정
   - execute_shell: 명령어 실행 (테스트, 설치 등)
   - list_files: 디렉토리 확인
4. 이미 존재하는 파일을 수정할 때는 반드시 먼저 읽는 단계를 포함하라.
5. 코드를 작성한 후에는 반드시 검증(테스트) 단계를 포함하라.

[Output Schema (Strict JSON)]
반드시 다음 JSON 구조를 준수하라:
{{
  "thought_process": "현재 상황 분석 및 계획 수립 이유",
  "goal": "최종 달성 목표 요약",
  "steps": [
    {{"id": 1, "action": "tool_name", "target": "file_path_or_command", "reason": "구체적인 이유"}}
  ]
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
        response_schema={
            "type": "OBJECT",
            "properties": {
                "thought_process": {"type": "STRING"},
                "goal": {"type": "STRING"},
                "steps": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "id": {"type": "INTEGER"},
                            "action": {
                                "type": "STRING", 
                                "enum": ["read_file", "write_file", "execute_shell", "list_files"]
                            },
                            "target": {"type": "STRING"},
                            "reason": {"type": "STRING"}
                        },
                        "required": ["id", "action", "target", "reason"]
                    }
                }
            },
            "required": ["thought_process", "goal", "steps"]
        }
    )

    # 3. Gemini 호출
    response = auth.generate(
        model_id="gemini-3-flash-preview", # 복잡한 계획 수립을 위해 고성능 모델 사용
        contents=state["messages"],
        config=config
    )

    try:
        # JSON 파싱
        # google-genai 0.3.0+ 에서는 response.parsed가 지원될 수 있으나 안전하게 text 파싱도 고려
        plan_data = response.parsed if hasattr(response, 'parsed') else json.loads(response.text)
        
        logger.info(f"Planner Thought: {plan_data.get('thought_process')}")
        logger.info(f"Plan Goal: {plan_data.get('goal')}")
        
        # Plan을 상태에 저장하고 Coder에게 넘김
        # steps 리스트를 문자열 리스트로 변환하거나 구조체 그대로 넘길 수 있음.
        # State 정의상 plan: List[str] 이므로, step을 문자열 표현으로 변환하거나 State 정의를 유연하게 써야 함.
        # 여기서는 편의상 JSON dump된 문자열 리스트로 저장하거나, 그냥 객체로 넘기기 위해 State 수정을 고려할 수도 있지만,
        # 일단 문자열로 변환하여 저장. (Coder가 이를 파싱해서 쓰도록)
        
        # 하지만 GortexState 정의를 보면 `plan: List[str]` 이다.
        # Coder 구현 편의를 위해 각 step을 JSON 문자열로 저장하는 것이 좋겠다.
        plan_steps = [json.dumps(step, ensure_ascii=False) for step in plan_data["steps"]]
        
        return {
            "plan": plan_steps,
            "current_step": 0,
            "next_node": "coder",
            "messages": [("ai", f"계획을 수립했습니다: {plan_data.get('goal')} ({len(plan_steps)} steps)")]
        }

    except Exception as e:
        logger.error(f"Error parsing planner response: {e}")
        return {
            "next_node": "__end__", 
            "messages": [("ai", f"계획 수립 중 오류가 발생했습니다: {e}")]
        }
