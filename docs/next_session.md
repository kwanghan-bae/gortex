# Next Session

## Session Goal
- 3D 의존성 군집화 및 클러스터 시각화 (Dependency Clustering v1)

## Context
- 시스템이 복잡해짐에 따라 3D 그래프의 노드 개수가 늘어나 가독성이 떨어짐.
- 서로 밀접하게 연결된 노드(예: Auth 관련 파일들, UI 관련 노드들)를 하나의 시각적 그룹(Cluster)으로 묶어 표현하여 거시적인 아키텍처 조망을 지원해야 함.

## Scope
### Do
- `ui/three_js_bridge.py`에 노드들 간의 거리를 계산하여 그룹 ID를 부여하는 클러스터링 로직 추가.
- 웹 대시보드 3D 뷰에서 그룹별로 배경 박스나 고유 색상을 입혀 시각적으로 구분.
- 영향 범위 분석 시, 특정 클러스터 전체가 하이라이트되는 상위 레벨 시각화 지원.

### Do NOT
- 실시간 렌더링 성능을 저해할 정도의 복잡한 물리 계산은 지양할 것 (단순 거리/연결성 기반).

## Expected Outputs
- `ui/three_js_bridge.py`, `ui/web_server.py` 수정.

## Completion Criteria
- 웹 대시보드 실행 시, 흩어진 노드들이 특정 의미 단위로 묶여서(Clustered) 시각적으로 표시되는 것이 확인되어야 함.
