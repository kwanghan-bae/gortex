# Next Session

## Session Goal
- 에이전트 프롬프트 외부 템플릿화 및 동적 관리 (Dynamic Prompting v1)

## Context
- 현재 `Manager`, `Planner`, `Coder` 등의 시스템 지침(Instruction)이 파이썬 코드 내부에 f-string으로 내장되어 있어, 지시사항 하나를 고치기 위해 코드를 수정하고 세션을 재시작해야 함.
- 프롬프트를 외부 파일(`docs/prompts/*.yaml`)로 분리하여 관리하고, 에이전트 실행 시 이를 동적으로 로드하여 주입하는 아키텍처가 필요함.

## Scope
### Do
- `gortex/docs/prompts/` 디렉토리 생성 및 각 에이전트별 기본 프롬프트 템플릿 작성.
- `utils/prompt_loader.py` 유틸리티를 추가하여 템플릿 로드 및 변수 치환 로직 구현.
- 모든 에이전트 노드가 이 로더를 사용하여 시스템 지침을 획득하도록 수정.

### Do NOT
- 기존의 정교한 프롬프트 내용을 단순화하지 말 것 (내용은 유지하되 위치만 이동).

## Expected Outputs
- `docs/prompts/*.yaml` 파일들, `utils/prompt_loader.py`, 에이전트 파일들 수정.

## Completion Criteria
- 코드 내의 하드코딩된 대규모 프롬프트 문자열이 사라지고, 외부 파일을 통한 동적 주입이 정상 작동하는 것이 확인되어야 함.
