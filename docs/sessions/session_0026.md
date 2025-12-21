# Session 0026

## Goal
- 지식 간 상관관계 분석 및 지식 지도 구축 (Knowledge Relation Mapper v1)

## What Was Done
- **utils/vector_store.py 수정**: 지식 항목들 간의 연결 정보를 보관하기 위한 `links` 필드 추가.
- **agents/analyst.py 수정**: 모든 지식을 전수 조사하여 벡터 유사도가 0.85 이상인 항목들을 자동 연결하는 `map_knowledge_relations` 메서드 구현 및 노드 통합.
- **ui/three_js_bridge.py 수정**: 지식 노드 간의 상관관계(`links`)를 추적하여 3D 연결선(correlation 타입)을 생성하는 시각화 로직 보강.
- **연속성 확보**: 이제 시스템은 개별 지식 파편을 넘어, 지식 간의 입체적인 연결망을 형성하여 더 깊은 추론이 가능해짐.

## Decisions
- 지식 연결의 임계값을 0.85로 설정하여, 의미가 매우 밀접한 지식들만 관계를 맺도록 함으로써 지식 지도의 가독성을 확보함.
- 매 분석 요청 시마다 지식 정리를 수행하도록 하여 지식 베이스의 자기 조직화(Self-Organization)를 유지함.

## Problems / Blockers
- 지식 항목이 기하급수적으로 늘어날 경우, O(n^2) 복잡도를 가진 전수 조사 방식은 성능 한계에 부딪힐 수 있음. 향후 인덱싱 기반의 부분 검색 및 배치 처리 로직으로 고도화 필요.

## Notes for Next Session
- 시스템의 '사회적 지성'을 한 단계 더 높이기 위해, 현재 에이전트들이 내린 결정과 지식 활용 내역을 바탕으로 사용자의 다음 행동을 시각적으로 유도하고 학습하는 'User Workflow Steering' 기능이 필요함.
