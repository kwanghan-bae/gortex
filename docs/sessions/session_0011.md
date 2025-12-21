# Session 0011

## Goal
- 에이전트 추론 인과 관계 시각화 (Causal Graph Explorer v1)

## What Was Done
- **core/observer.py 수정**: 전체 로그의 `cause_id`를 추적하여 구조화된 인과 관계 그래프(Nodes/Edges)를 생성하는 `get_causal_graph` 메서드 구현.
- **ui/three_js_bridge.py 수정**: 인과 그래프 데이터를 시간축 기반의 3D 공간에 배치하고 에이전트별 색상을 할당하는 `convert_causal_graph_to_3d` 로직 구현.
- **main.py 수정**: 매 턴 종료 후 인과 관계 그래프를 웹 대시보드로 실시간 스트리밍하는 파이프라인 구축.

## Decisions
- 인과 관계 그래프의 X축을 이벤트 발생 순서로 설정하여 시간 흐름에 따른 '사고의 계보'를 직관적으로 파악하게 함.
- 노드 겹침을 방지하기 위해 Y, Z축에 수학적 변동(Sin/Cos)을 주어 토폴로지 가독성을 확보함.

## Problems / Blockers
- 로그가 수천 개 이상 쌓일 경우 그래프 렌더링 성능 저하가 우려됨. 향후 최근 N개의 이벤트만 보여주는 'Rolling Window' 또는 페이징 처리 필요.

## Notes for Next Session
- 시스템이 고도화됨에 따라, 이제 사용자가 자연어로 복잡한 아키텍처 규칙을 정의하면 이를 검증해주는 'Constraint Validator' 기능이 필요함.
