# Next Session

## Session Goal
- 에이전트 도구 메시지 전면 i18n 마이그레이션 (Message Integration v1)

## Context
- v2.6.8에서 로컬라이징 엔진의 기반이 마련됨.
- 현재 `Planner`의 "계획을 수립했습니다", `Coder`의 "Step 완료" 등 파편화된 메시지들이 여전히 파이썬 코드 내부에 하드코딩되어 있음.
- 모든 에이전트 노드 및 도구 호출 결과를 `i18n.t` 기반으로 전환하여 설정 언어에 따른 완벽한 일관성을 확보해야 함.

## Scope
### Do
- `docs/i18n/*.json`에 에이전트별 도구 실행 관련 키값 대량 추가.
- `agents/planner.py`, `agents/coder.py`, `agents/analyst.py`의 `messages.append` 부분 전수 조사 및 수정.
- `/language` 명령어로 언어 전환 시 모든 대화 흐름이 자연스럽게 바뀌는지 테스트.

### Do NOT
- 에이전트의 '고유 사고(Thought)'는 LLM 원문 그대로 두되, 시스템이 덧붙이는 접두사나 결과 요약 위주로 작업.

## Expected Outputs
- `docs/i18n/*.json` 업데이트, 모든 에이전트 노드 파일 수정.

## Completion Criteria
- 시스템의 모든 응답과 로그가 설정된 언어(ko/en)에 따라 100% 일관되게 출력되는 것이 확인되어야 함.
