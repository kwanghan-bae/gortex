# Next Session

## Session Goal
- **Automated Dependency Analysis & Clustering Visualization**: 3D Bridge(`ui/three_js_bridge.py`)를 고도화하여, 시스템의 모듈 간 의존성을 분석하고 이를 시각적으로 군집화(Clustering)하여 보여주는 기능을 구현한다.

## Context
- 현재 TUI/Web Bridge는 노드와 엣지를 보여주지만, 모듈 간의 "강한 결합"이나 "논리적 그룹"을 시각적으로 구분해주지는 못함.
- `AnalystAgent`의 `audit_architecture` 결과를 시각화 레이어에 반영하여, 의존성이 복잡한 곳을 한눈에 파악할 수 있게 해야 함.

## Scope
### Do
- `ui/three_js_bridge.py`: `convert_dependency_graph` 메서드를 확장하여 Louvain 또는 간단한 군집 알고리즘을 적용, `group` 속성을 노드에 부여.
- `agents/analyst/base.py`: 의존성 그래프 추출 시 모듈 간 가중치(호출 빈도 등)를 계산하여 그래프 데이터에 포함.
- `ui/dashboard.py`: 클러스터링된 데이터를 웹 브릿지로 전송하는 파이프라인 연결.

### Do NOT
- 복잡한 3D 렌더링 엔진 자체를 수정하지 않음 (데이터 구조 변경에 집중).

## Expected Outputs
- `ui/three_js_bridge.py` (Update)
- `agents/analyst/base.py` (Update)

## Completion Criteria
- 웹 대시보드로 전송되는 JSON 데이터에 `nodes` 배열의 각 요소가 `group` 또는 `cluster_id`를 포함해야 함.
- `docs/sessions/session_0081.md` 기록.