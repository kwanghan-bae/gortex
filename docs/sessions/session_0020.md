# Session 0020

## Goal
- 파일 수정 영향 범위의 3D 시각적 하이라이트 (Visual Impact v1)

## What Was Done
- **agents/planner.py 수정**: `impact_analysis` 필드를 구조화된 데이터(JSON)로 반환하도록 스키마 및 메시지 포맷 개선.
- **ui/three_js_bridge.py 수정**: 분석된 영향 범위 데이터(`direct`, `indirect`, `target`)를 바탕으로 3D 노드들에 붉은색 Glow 하이라이트를 입히는 `apply_impact_highlight` 메서드 구현.
- **main.py 수정**: Planner의 출력에서 영향 분석 데이터를 포착하여 웹 대시보드 그래프에 리스크 가시화를 즉시 적용하도록 연동.

## Decisions
- 위험 노드는 타겟(강렬한 빨강, 2.0배 확대), 직접 영향(빨강, 1.5배 확대), 간접 영향(연한 빨강, 1.2배 확대)으로 단계별 시각화를 적용하여 리스크의 강도를 구분함.
- `Planner`가 반환하는 구조화된 데이터를 시스템 메시지로 변환할 때, 기술적인 파일 목록을 가독성 있게 나열하도록 개선함.

## Problems / Blockers
- 현재 하이라이트는 매 턴 갱신되지만, 여러 에이전트가 동시에 다른 파일을 건드릴 경우 하이라이트가 충돌하거나 덮어씌워질 가능성이 있음. 향후 세션 단위의 '누적 리스크 맵' 관리 필요.

## Notes for Next Session
- 시스템의 '언어 지능'을 한 단계 더 높이기 위해, 현재 한글/영어 위주의 지원을 넘어 모든 에이전트 출력과 문서를 실시간으로 다국어 번역하여 제공하는 'Omni-Translator' 웹 UI 통합이 필요함.
