# Next Session

## Session Goal
- **Self-Healing Documentation System**: `AnalystAgent`가 코드베이스와 문서 간의 불일치(Drift)를 감지하고, 문서를 자동으로 최신화하는 기능을 구현한다.

## Context
- `Session 0083`에서 README를 개편했지만, `TECHNICAL_SPEC.md` 등 기술 문서는 코드 변경 사항(예: `GortexState` 구조 변경)을 따라가지 못할 위험이 큼.
- 진화하는 시스템은 스스로 문서를 유지보수해야 함.

## Scope
### Do
- `agents/analyst/reflection.py`: `check_documentation_drift(file_path, doc_path)` 메서드 구현.
    - Python `ast` 모듈을 사용하여 클래스/TypedDict 구조 파싱.
    - 문서 내 코드 블록(Markdown)과 비교.
- `docs/TECHNICAL_SPEC.md` vs `core/state.py` 동기화 테스트.

### Do NOT
- 모든 문서를 한 번에 처리하지 않음 (Pilot: Technical Spec).

## Expected Outputs
- `agents/analyst/reflection.py` (Update)
- `docs/TECHNICAL_SPEC.md` (Auto-updated if drift detected)

## Completion Criteria
- `core/state.py`에 더미 필드를 추가했을 때, Analyst가 이를 감지하고 `TECHNICAL_SPEC.md`를 수정해야 함.
- `docs/sessions/session_0084.md` 기록.