# Session 0013

## Goal
- 에이전트 도구 호출 전후의 시스템 상태 전이 시각화 (Visual Simulation v2)

## What Was Done
- **agents/coder.py 수정**: `simulation` 스키마 내에 `expected_graph_delta` 필드를 추가하여, 예상되는 아키텍처 변화(노드 추가/수정/삭제)를 구조화된 데이터로 생성하도록 고도화.
- **ui/three_js_bridge.py 수정**: 예상 델타 데이터를 반투명한 '고스트 노드'와 '점선 연결선'으로 변환하는 `convert_simulation_to_3d` 메서드 구현.
- **main.py 수정**: 도구 실행 전 예상 시뮬레이션 데이터를 웹 대시보드로 실시간 스트리밍하는 로직 연동.

## Decisions
- 시뮬레이션 데이터는 기존 인과 그래프와 시각적으로 명확히 구분하기 위해 낮은 투명도(Opacity 0.4)와 흰색 고스트 스타일을 적용함.
- 미래 상태(Preview)를 현재의 사고 흐름 마지막 노드에 연결하여 인과 관계의 연속성을 표현함.

## Problems / Blockers
- 복잡한 델타의 경우 고스트 노드들이 겹칠 수 있음. 향후 더 정교한 3D 레이아웃 엔진(예: Force-directed layout) 도입 필요.

## Notes for Next Session
- 시스템의 '협업 지능'을 한 단계 더 높이기 위해, 에이전트들이 작업 도중 발생한 의사결정의 트레이드오프를 사용자에게 질문하고 답변을 지식화하는 'Interactive Decision Learning' 기능이 필요함.
