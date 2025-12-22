# Next Session

## Session Goal
- **Self-Healing Documentation System**: `AnalystAgent`가 코드베이스의 최신 상태(함수 시그니처, 클래스 구조 등)를 스캔하여, `docs/TECHNICAL_SPEC.md`와 같은 기술 문서와의 불일치를 자동으로 감지하고 수정 제안을 생성하는 기능을 구현한다.

## Context
- 코드는 빠르게 변하지만 문서는 뒤쳐지기 쉬움(Documentation Drift).
- 진화하는 AI 시스템의 특성상, 스스로 문서를 유지보수하는 능력이 필수적임.
- 특히 `TECHNICAL_SPEC.md`의 데이터 구조 정의가 실제 `TypedDict` 정의와 일치하는지 검증 필요.

## Scope
### Do
- `agents/analyst/reflection.py`: `check_documentation_drift` 메서드 구현.
    - 주요 모듈(`core/state.py`, `core/auth.py` 등)의 AST를 파싱하여 실제 구조 추출.
    - 문서 내 코드 블록이나 표와 비교.
- `agents/analyst/base.py`: 감지된 드리프트를 기반으로 문서 업데이트 패치 생성.

### Do NOT
- 모든 문서를 대상으로 하지 않음 (우선 `TECHNICAL_SPEC.md`와 `core/*.py` 간의 동기화에 집중).

## Expected Outputs
- `agents/analyst/reflection.py` (Update)
- `docs/TECHNICAL_SPEC.md` (Self-healed if drift detected)

## Completion Criteria
- `core/state.py`의 `GortexState` 정의가 변경되었을 때, Analyst가 이를 감지하고 리포트해야 함.
- `docs/sessions/session_0083.md` 기록.