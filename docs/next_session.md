# Next Session

## Session Goal
- 파일 수정 영향 범위의 3D 시각적 하이라이트 (Visual Impact v1)

## Context
- `Dependency Impact Analyzer`가 영향 받는 파일 목록을 텍스트로 잘 보고하고 있으나, 3D 그래프와 연동되지 않아 공간적인 리스크 파악이 어려움.
- 수정 타겟이 결정되면, 웹 대시보드에서 해당 노드와 직접/간접적으로 연결된 모든 노드를 붉은색으로 하이라이트 처리하여 위험 범위를 가시화해야 함.

## Scope
### Do
- `ui/three_js_bridge.py`에 특정 노드와 연결된 노드들을 찾아 시각적 속성(Color, Glow)을 변경하는 `highlight_impact_nodes` 로직 추가.
- `main.py`에서 `Planner`의 `impact_analysis` 데이터를 가공하여 시각화 파이프라인으로 스트리밍 연동.
- 웹 클라이언트에서 실시간으로 위험 지점이 강조되도록 데이터 스키마 보강.

### Do NOT
- 기존의 인과 관계 그래프 레이아웃을 무너뜨리지 말 것 (속성 변경 위주).

## Expected Outputs
- `ui/three_js_bridge.py`, `main.py` 수정.

## Completion Criteria
- 파일 수정 계획 수립 시, 웹 대시보드의 3D 노드들이 빨간색으로 빛나며 위험 범위를 표시하는 것이 확인되어야 함.