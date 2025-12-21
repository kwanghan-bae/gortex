# Next Session

## Session Goal
- 모든 에이전트 지침의 외부 템플릿 통합 (Global Dynamic Prompting v1)

## Context
- v2.5.8에서 `Manager`와 `PromptLoader`가 완성됨.
- 이제 `Planner`, `Coder`, `Analyst`, `Researcher` 등 나머지 모든 노드에 대해서도 하드코딩된 프롬프트를 제거하고 `docs/prompts/*.yaml` 기반으로 전환해야 함.

## Scope
### Do
- `docs/prompts/core_agents.yaml`에 Planner, Coder, Analyst, Researcher의 상세 지침 추가.
- `agents/planner.py`, `agents/coder.py`, `agents/analyst.py`, `agents/researcher.py`를 수정하여 `PromptLoader` 연동.
- 템플릿 변수(예: `{current_files}`, `{tool_output}` 등)를 각 노드 맥락에 맞게 매핑.

### Do NOT
- 각 에이전트의 고유한 로직(Python Code)은 건드리지 말고, 지침(Instruction) 문자열만 이전할 것.

## Expected Outputs
- `docs/prompts/core_agents.yaml` 업데이트, 모든 에이전트 파일 수정.

## Completion Criteria
- 모든 에이전트 노드에서 하드코딩된 대규모 지침 문자열이 완전히 제거되고, 외부 파일로부터 지능을 로드하는 것이 확인되어야 함.