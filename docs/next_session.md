# Next Session

## Session Goal
- 지식 저장소 파티셔닝 및 성능 최적화 (Memory Sharding v1)

## Context
- `LongTermMemory`가 단일 JSON 파일(`long_term_memory.json`)로 관리되고 있어, 지식이 수천 건 이상 쌓일 경우 로딩 및 검색 속도가 급격히 저하될 우려가 있음.
- 프로젝트 단위(Namespace) 또는 주제별로 지식을 샤딩(Sharding)하여 저장하고, 필요한 샤드만 메모리에 로드하여 검색하는 지능형 파티셔닝이 필요함.

## Scope
### Do
- `utils/vector_store.py`를 확장하여 `namespace` 기반의 샤딩 로직 구현.
- `memorize` 시 현재 프로젝트나 맥락에 맞는 샤드 파일로 자동 분산 저장.
- `recall` 시 관련성 높은 샤드를 우선 탐색하는 멀티 샤드 검색 루틴 추가.

### Do NOT
- 복잡한 데이터베이스 엔진을 도입하지 말 것 (파일 기반 샤딩 유지).

## Expected Outputs
- `utils/vector_store.py`, `agents/manager.py` 수정.

## Completion Criteria
- 지식 저장 시 `logs/memory/shard_XXX.json` 형태로 분할 저장되고, 검색 시 정확한 샤드에서 지식이 소환되는 것이 확인되어야 함.