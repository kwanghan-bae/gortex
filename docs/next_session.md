# Next Session

## Session Goal
- **Intelligent Task Chaining & Handoff**: 에이전트 간 노드 전환 시, 단순히 다음 순서로 넘어가는 것이 아니라 이전 에이전트가 다음 주자에게 전달하는 구체적인 '인수인계 지침(Handoff Instruction)'을 생성하여 작업의 맥락과 정밀도를 극대화한다.

## Context
- 현재 에이전트들은 `messages`와 `plan`을 공유하지만, 직전 단계에서 발견한 미묘한 뉘앙스나 주의사항을 명시적으로 전달하는 통로가 부족함.
- 예: `Planner`가 계획을 짤 때 "A 파일을 수정할 때는 B 함수의 부수 효과를 꼭 확인하라"는 메시지를 `Coder`에게 직접 귓속말 하듯 전달해야 함.
- 이는 다중 에이전트 협업의 '지능적 연결성'을 강화함.

## Scope
### Do
- `core/state.py`: `handoff_instruction` 필드 추가.
- `agents/planner.py` & `agents/coder.py`: 작업 완료 시 다음 에이전트를 위한 지침을 작성하도록 로직 보강.
- `utils/prompt_loader.py`: `handoff_instruction`이 있을 경우 시스템 프롬프트 최상단에 강조하여 주입.

### Do NOT
- 모든 노드 조합에 대해 복잡한 핸드오프 로직을 짜지 않음 (우선 Planner -> Coder, Coder -> Analyst 위주).

## Expected Outputs
- `core/state.py` (Update)
- `agents/planner.py` (Update)
- `utils/prompt_loader.py` (Update)
- `tests/test_handoff_instruction.py` (New)

## Completion Criteria
- `Planner` 실행 후 `GortexState`에 `handoff_instruction`이 생성되어야 함.
- `Coder`가 해당 지침을 인식하고 작업에 반영하는지 로그로 확인.
- `docs/sessions/session_0098.md` 기록.