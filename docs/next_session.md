# Next Session

## Session Goal
- 실시간 API 문서 학습 및 기술 활용 (Live Documentation Learning v1)

## Context
- 에이전트가 새로운 라이브러리를 사용하거나 기존 로직을 최신 버전으로 업데이트할 때, 내부 지식만으로는 한계가 있음.
- `Researcher`를 통해 특정 라이브러리의 공식 문서(또는 API Reference)를 실시간으로 검색하여 핵심 시그니처를 지식화하고, 이를 작업에 즉시 반영해야 함.

## Scope
### Do
- `agents/researcher.py`에 공식 문서를 타겟팅하여 스캔하는 `fetch_live_docs` 메서드 추가.
- `agents/planner.py`에서 계획 수립 시 '문서 학습' 단계를 전략적으로 제안하도록 지침 보강.
- 학습된 문서를 `LongTermMemory`에 임시 저장하여 `Coder`가 참조할 수 있게 함.

### Do NOT
- 대규모 사이트 전체 크롤링 금지 (특정 API 페이지 한정).

## Expected Outputs
- `agents/researcher.py`, `agents/planner.py` 수정.

## Completion Criteria
- 새로운 라이브러리 사용 요청 시, Researcher가 문서를 검색하여 요약하고 Coder가 해당 요약을 바탕으로 정확한 코드를 작성하는 것이 확인되어야 함.
