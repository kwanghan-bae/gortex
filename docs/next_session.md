# Next Session

## Session Goal
- **Autonomous Post-Session Reflection**: 매 세션 종료 시 작성된 활동 기록(`docs/sessions/session_XXXX.md`)을 정밀 분석하여, 단순한 활동 나열을 넘어 시스템이 미래에 지켜야 할 명확한 지침(`Experience Rules`)으로 추출 및 승격시키는 지능을 구현한다.

## Context
- 현재 세션 기록은 사람이 읽기엔 좋지만, AI가 즉각적으로 학습에 활용하기에는 비정형적임.
- "이런 문제가 있어서 이렇게 해결했다"는 기록을 "앞으로 이럴 때는 이렇게 하라"는 규칙으로 변환해야 진정한 자가 진화가 완성됨.
- `Analyst` 에이전트의 성찰(Reflection) 능력을 세션 단위로 확장함.

## Scope
### Do
- `agents/analyst/reflection.py`: `reflect_on_session_docs` 메서드 추가.
- `agents/analyst/reflection.py`: 세션 문서에서 'Issues & Resolutions' 섹션을 파싱하여 `Experience Rules` 후보 도출.
- `main.py`: 세션 종료 루틴에 사후 성찰 단계를 공식적으로 추가.

### Do NOT
- 모든 과거 세션을 소급 적용하지 않음 (가장 최근 세션 위주로 시작).

## Expected Outputs
- `agents/analyst/reflection.py` (Update)
- `experience.json` (Auto-updated with rules from session docs)
- `tests/test_session_reflection.py` (New)

## Completion Criteria
- 특정 세션 문서에 "API 404 에러 해결" 기록이 있을 때, 성찰 후 `experience.json`에 관련 모델 명명 규칙이 자동 저장되어야 함.
- `docs/sessions/session_0097.md` 기록.
