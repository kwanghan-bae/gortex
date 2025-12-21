# Next Session

## Session Goal
- 작업 완료 자동 기록 및 문서 갱신 (Auto-Finalizer v1)

## Context
- 현재는 에이전트가 작업을 마친 후 문서 업데이트(Release Note, Session Record)를 제가 수동으로 수행하거나 별도의 단계로 처리하고 있음.
- 에이전트가 "미션 완료"를 선언하는 즉시, 스스로 이번 세션에서 한 일을 요약하고 `release_note.md`와 `session_XXXX.md`를 작성하는 자율적 정리 기능이 필요함.

## Scope
### Do
- `agents/analyst.py`에 세션 전체 활동을 요약하여 문서를 작성하는 `auto_finalize_session` 메서드 추가.
- `main.py` 종료 시 또는 미션 완료 선언 시 이 메서드를 자동으로 트리거함.
- `next_session.md`까지 자동으로 갱신하여 다음 작업을 준비함.

### Do NOT
- 사용자의 최종 승인 없이 `main.py`를 완전히 종료하지 말 것 (기록 완료 후 대기).

## Expected Outputs
- `agents/analyst.py`, `main.py` 수정.

## Completion Criteria
- 에이전트가 작업을 마쳤을 때, `docs/` 하위의 모든 관련 문서가 최신화되어 있는 것이 확인되어야 함.