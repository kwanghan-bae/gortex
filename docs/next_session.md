# Next Session

## Session Goal
- **Intelligent API Key Rotation & Health Check**: 여러 Gemini API Key의 상태와 할당량(Quota)을 실시간으로 감시하고, 에러나 속도 제한(429) 발생 시 가장 건강한 키로 즉각 전환하며, 키별 쿨다운(Cooldown) 시간을 지능적으로 관리하는 '무중단 인증 관리 엔진'을 구축한다.

## Context
- 현재 Gortex는 `core/auth.py`에서 키 로테이션을 수행하지만, 단순히 순차적(Round-robin)으로 전환하거나 고정된 Jitter 대기 시간을 가짐.
- 특정 키가 할당량 소진 시 전체 시스템이 지연되는 현상을 방지하기 위해, 각 키의 '건강 상태'와 '잔여 수명'을 추적해야 함.
- 이는 대규모 작업이나 다중 에이전트 동시 실행 시 시스템의 안정성을 보장하는 핵심 인프라임.

## Scope
### Do
- `core/auth.py`: 키별 성공률과 할당량 상태를 기록하는 `KeyHealthMonitor` 클래스 추가.
- `core/auth.py`: 에러 타입(429 vs 500)에 따라 서로 다른 쿨다운 전략을 적용하는 `AdaptiveRotationStrategy` 구현.
- `ui/dashboard.py`: 현재 활성화된 키의 상태와 전체 키 번들의 건강도를 보여주는 인증 감시 위젯 추가.

### Do NOT
- 실제 Gemini API의 내부 할당량 조회 API 연동은 배제하고(지원하지 않을 수 있음), 시스템 내부 에러 로그를 기반으로 추정함.

## Expected Outputs
- `core/auth.py` (Key Health Monitor & Adaptive Rotation)
- `ui/dashboard.py` (Auth Status Widget)
- `tests/test_auth_rotation.py` (New)

## Completion Criteria
- 특정 키에서 429 에러가 발생했을 때, 해당 키가 즉시 'Cooldown' 상태로 전환되고 5초 이내에 다른 건강한 키로 교체되어야 함.
- 쿨다운 중인 키는 지정된 시간이 지나기 전까지 로테이션 대상에서 제외되어야 함.
- `docs/sessions/session_0124.md` 기록.