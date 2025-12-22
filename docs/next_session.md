# Next Session

## Session Goal
- **Automated API Key Health Check & Rotation**: 빈번한 429 에러(할당량 초과)에 대응하여, 사용 전 API 키의 상태를 실시간 체크하고 문제가 발생한 키를 일정 시간 동안 제외(Cooldown)하는 견고한 로테이션 시스템을 구축한다.

## Context
- 최근 여러 세션에서 API 할당량 부족으로 인한 실패가 반복됨.
- 현재 로테이션은 단순한 순차 전환 방식이라, 이미 소진된 키로 다시 돌아가는 문제가 있음.
- 키별로 '마지막 사용 시간'과 '실패 이력'을 관리하여 지능적으로 모델을 공급해야 함.

## Scope
### Do
- `core/auth.py`: `check_key_status` 메서드 추가 (ListModels 호출 등으로 유효성 확인).
- `core/auth.py`: `KeyPool` 클래스 도입 (Cooldown 로직, 가중치 로테이션 등).
- `core/llm/gemini_client.py`: 새롭게 강화된 로테이션 엔진 연동.

### Do NOT
- 새로운 외부 API 제공자(Anthropic 등) 연동은 이 세션에서 다루지 않음 (Gemini 최적화 집중).

## Expected Outputs
- `core/auth.py` (Refactored)
- `tests/test_auth_rotation.py` (New)

## Completion Criteria
- 키 하나를 강제로 무효화(429 발생)했을 때, 시스템이 이를 감지하고 일정 시간 동안 해당 키를 후보에서 제외해야 함.
- `docs/sessions/session_0094.md` 기록.