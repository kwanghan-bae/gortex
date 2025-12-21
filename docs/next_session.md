# Next Session

## Session Goal
- 에이전트 페르소나 동적 관리 및 생성 (Persona Lab v1)

## Context
- v2.3.0에서 도입된 '토론 페르소나(Innovation, Stability)'가 현재는 코드 내에 하드코딩되어 있어 확장이 어려움.
- 사용자가 상황에 맞는 새로운 페르소나(예: 'Security Expert', 'UX Specialist')를 정의하고, Manager가 이를 필요에 따라 에이전트에게 할당할 수 있는 관리 체계가 필요함.

## Scope
### Do
- `gortex/docs/PERSONAS.md` 파일을 생성하여 시스템 페르소나 카탈로그 구축.
- `agents/manager.py`가 상황에 따라 적절한 페르소나 조합을 선택하도록 로직 고도화.
- `agents/swarm.py`에서 `PERSONAS.md`에 정의된 페르소나 지침을 동적으로 읽어와 프롬프트에 주입.

### Do NOT
- 기존의 기본적인 페르소나(Innovation, Stability) 삭제 금지 (기본값으로 유지).

## Expected Outputs
- `docs/PERSONAS.md` 생성, `agents/manager.py`, `agents/swarm.py` 수정.

## Completion Criteria
- 새로운 페르소나를 `PERSONAS.md`에 추가했을 때, 토론 시 해당 페르소나의 지침이 프롬프트에 반영되는 것이 로그로 확인되어야 함.
