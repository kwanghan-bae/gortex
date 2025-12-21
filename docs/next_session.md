# Next Session

## Session Goal
- 에이전트 추론 인과 관계 시각화 (Causal Graph Explorer v1)

## Context
- 다중 에이전트 협업과 토론이 복잡해지면서, 최종 결과의 근본 원인을 파악하기가 점점 어려워지고 있음.
- `logs/trace.jsonl`에 기록된 `cause_id`를 활용하여, 특정 결정이 어떤 사고 과정과 도구 호출로부터 비롯되었는지 보여주는 인과 관계 그래프 데이터 파이프라인이 필요함.

## Scope
### Do
- `core/observer.py` (또는 관련 로직)를 확장하여 전체 세션의 인과 관계 체인을 그래프 데이터(Nodes/Edges)로 변환하는 기능 구현.
- `ui/three_js_bridge.py`에 인과 관계 그래프를 3D 토폴로지로 변환하는 로직 추가.
- 웹 대시보드로 실시간 인과 관계 데이터를 전송하여 시각화.

### Do NOT
- 기존의 단순 사고 트리 시각화 로직과 혼동하지 말 것 (인과 관계는 세션 전체를 관통함).

## Expected Outputs
- `core/observer.py`, `ui/three_js_bridge.py`, `main.py` 수정.

## Completion Criteria
- 웹 대시보드에서 특정 노드를 선택했을 때, 그 노드의 원인이 된 이전 이벤트들이 강조되어 표시되는 것이 확인되어야 함.
