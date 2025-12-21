# Next Session

## Session Goal
- 에이전트 페르소나 프로필 구축 및 동적 전환 (Dynamic Persona Switch v1)

## Context
- 현재 에이전트들은 정해진 지침(Instruction)만 따르고 있어, 문제 해결 방식이 다소 경직되어 있음.
- `Innovation(혁신가)`, `Stability(안정주의자)`, `Security Expert(보안 전문가)`, `UX Specialist(사용자 경험 전문가)` 등 다양한 페르소나 프로필을 `docs/i18n/personas.json`에 정의하고, 작업의 성격에 따라 에이전트에게 주입해야 함.

## Scope
### Do
- `docs/i18n/personas.json` 생성 및 4종 이상의 핵심 페르소나 정의.
- `agents/manager.py`에서 작업 분석 시 최적의 페르소나를 결정하여 `state["assigned_persona"]`로 전달하는 로직 추가.
- `docs/prompts/core_agents.yaml`을 수정하여 전달받은 페르소나를 시스템 지침에 동적으로 합성.

### Do NOT
- 모든 작업에 페르소나를 강제하지 말 것 (기본값: Standard).

## Expected Outputs
- `docs/i18n/personas.json`, `agents/manager.py`, `docs/prompts/core_agents.yaml` 수정.

## Completion Criteria
- 보안 관련 요청 시 '보안 전문가' 페르소나가 주입되고, UI 관련 요청 시 'UX 전문가' 페르소나가 주입되어 사고 트리(`thought_tree`)의 내용이 해당 성격에 맞춰 변화하는 것이 확인되어야 함.