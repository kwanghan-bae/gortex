# Next Session

## Session Goal
- 지식 베이스 최적화 및 가비지 컬렉션 (Knowledge GC v1)

## Context
- `LongTermMemory`에 트렌드와 합의 교훈이 계속 쌓이면서, 유사한 지식이 중복 저장되거나 과거의 잘못된 정보가 남을 우려가 있음.
- 지식의 사용 빈도(`usage_count`)와 최신성(`timestamp`)을 기준으로 지식 베이스를 정기적으로 청소하는 메커니즘이 필요함.

## Scope
### Do
- `utils/vector_store.py`에 지식 항목별 `usage_count` 필드 추가 및 `recall` 시 카운트 증가 로직 추가.
- `AnalystAgent`에 `garbage_collect_knowledge` 메서드를 추가하여 불필요한 지식 삭제.
- `main.py` 부팅 시 또는 매 턴마다 자동으로 GC가 수행되도록 연동.

### Do NOT
- 중요한 아키텍처 결정이나 사용자가 명시적으로 저장한 매크로 삭제 금지.

## Expected Outputs
- `utils/vector_store.py`, `agents/analyst.py`, `main.py` 수정.

## Completion Criteria
- 중복되거나 오랫동안 사용되지 않은 지식이 자동으로 제거되고, 지식 베이스 파일 크기가 최적화되는 것이 확인되어야 함.