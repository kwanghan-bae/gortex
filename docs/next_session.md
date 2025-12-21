# Next Session

## Session Goal
- 지식 간 상관관계 분석 및 지식 지도 구축 (Knowledge Relation Mapper v1)

## Context
- `LongTermMemory`에 수많은 지식이 쌓였으나, 각 지식은 서로 독립적인 조각으로 존재함.
- "A 라이브러리 사용법"과 "B 아키텍처 규칙"이 서로 어떻게 연결되는지 분석하여, 에이전트가 지식을 소환할 때 관련 있는 다른 지식도 연쇄적으로 떠올리게(Spreading Activation) 해야 함.

## Scope
### Do
- `agents/analyst.py`에 지식 간의 유사도와 인과성을 분석하여 관계(Edges)를 생성하는 `map_knowledge_relations` 메서드 추가.
- `utils/vector_store.py`에 지식 간의 연결 정보를 저장할 `links` 필드 추가.
- 3D 지식 그래프에서 지식 노드 간의 상관관계를 선으로 시각화.

### Do NOT
- 모든 지식을 강제로 연결하지 말 것 (유사도 0.8 이상의 고관련 지식만 연결).

## Expected Outputs
- `agents/analyst.py`, `utils/vector_store.py`, `ui/three_js_bridge.py` 수정.

## Completion Criteria
- 웹 대시보드의 지식 그래프에서 특정 지식 노드를 선택했을 때, 관련 있는 다른 지식들이 연결되어 나타나는 것이 확인되어야 함.