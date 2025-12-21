# Next Session

## Session Goal
- 외부 기술 트렌드의 지식 베이스화 (Synaptic Knowledge Base v1)

## Context
- `TrendScout`이 매일 새로운 기술을 스캔하고 있으나, 그 데이터가 `tech_radar.json`에만 머물러 있어 실제 추론 시 깊이 있게 활용되지 못함.
- 스캔된 내용을 지식 단위(Snippets)로 분절하고, 이를 장기 기억(Vector Store)에 통합하여 모든 에이전트가 최신 기술 정보를 바탕으로 대화할 수 있게 해야 함.

## Scope
### Do
- `agents/trend_scout.py`에서 스캔된 트렌드를 `LongTermMemory`에 저장하는 로직 추가.
- `utils/vector_store.py` (또는 관련 유틸)를 확장하여 지식의 출처(Source: TrendScout)를 명시함.
- `agents/manager.py`가 사용자 요청 시 최신 트렌드 지식을 우선적으로 검색하도록 검색 가중치 조정.

### Do NOT
- 대규모 웹 크롤링 금지 (기존 TrendScout 검색 결과만 활용).

## Expected Outputs
- `agents/trend_scout.py`, `agents/manager.py` 수정.

## Completion Criteria
- TrendScout 실행 후, 새로운 기술 키워드에 대해 Manager가 "최신 트렌드에 따르면..."이라고 답변하는 것이 확인되어야 함.
