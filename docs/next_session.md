# Next Session

## Session Goal
- 3D 그래프 군집화 시각화 고도화 (Dependency Clustering v2)

## Context
- v2.6.7에서 기초적인 클러스터링(`cluster_id`)은 구현됨.
- 하지만 현재 노드 배치가 임의적이거나 시간축에만 의존하고 있어, 같은 클러스터끼리 뭉쳐 보이는 시각적 효과가 부족함.
- `ThreeJsBridge`에서 클러스터 ID를 기반으로 노드의 3D 좌표를 보정하여, 그룹별로 뚜렷한 영역을 가지도록 물리적 배치를 개선해야 함.

## Scope
### Do
- `ui/three_js_bridge.py`에서 클러스터 중심점(Centroid) 계산 로직 추가.
- 각 노드의 위치를 해당 클러스터 중심점 방향으로 인력(Attractive Force)을 가하여 재배치.
- 웹 UI 브로드캐스팅 시 클러스터별 경계 박스(Bounding Box) 데이터 포함.

### Do NOT
- 복잡한 물리 시뮬레이션 라이브러리를 사용하지 말 것 (단순 벡터 연산 유지).

## Expected Outputs
- `ui/three_js_bridge.py` 수정.

## Completion Criteria
- 웹 대시보드에서 같은 색상(클러스터)의 노드들이 시각적으로 군집을 형성하고, 그룹 간 경계가 명확해지는 것이 확인되어야 함.