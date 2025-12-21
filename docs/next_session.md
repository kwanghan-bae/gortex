# Next Session

## Session Goal
- 에이전트 도구 호출 전후의 시스템 상태 전이 시각화 (Visual Simulation v2)

## Context
- v2.0.7에서 도입된 `visual_delta` 시뮬레이션이 현재는 텍스트 기반의 예상 결과에 머물러 있음.
- 도구 호출 전 `Analyst` 또는 `Coder`가 변경될 것으로 예상되는 파일과 아키텍처 구조를 3D 그래프의 '미리보기(Preview)' 형태로 생성하고, 실제 결과와 비교하는 기능이 필요함.

## Scope
### Do
- `agents/coder.py`의 `simulation` 필드를 확장하여 예상되는 그래프 변화(`expected_graph_delta`)를 JSON 구조로 생성.
- `ui/three_js_bridge.py`에 시뮬레이션 데이터를 위한 고스트 노드(Ghost Nodes) 생성 로직 추가.
- 웹 대시보드에서 도구 실행 전 예상 시나리오를 점선 등으로 시각화.

### Do NOT
- 실제 파일 시스템을 건드리지 말 것 (철저히 가상 공간의 시뮬레이션).

## Expected Outputs
- `agents/coder.py`, `ui/three_js_bridge.py`, `main.py` 수정.

## Completion Criteria
- 도구 실행 전, 웹 대시보드에 변경 예정인 파일이나 노드가 '예상 상태'로 시각화되는 것이 확인되어야 함.
