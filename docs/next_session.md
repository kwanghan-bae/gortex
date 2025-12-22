# Next Session

## Session Goal
- **Agent Collaboration Heatmap**: 에이전트들 간의 데이터 교환, 호출 빈도, 성공적인 협업 횟수를 분석하여 대시보드 내에 히트맵(Heatmap) 또는 관계 매트릭스 형태로 시각화하고, 시스템의 병목 구간이나 가장 활발한 협업 시너지를 파악한다.

## Context
- v3.0 도입 이후 에이전트들이 동적으로 오케스트레이션되고 있으나, 그들 사이의 '관계'는 여전히 블랙박스 상태임.
- 어떤 에이전트가 어떤 에이전트와 자주 협력하는지, 그 과정에서 에러가 자주 발생하는지 시각화하여 최적화 근거로 활용함.

## Scope
### Do
- `core/observer.py`: 에이전트 간 'Caller-Callee' 관계 및 성공 여부를 기록하는 `log_collaboration` 메서드 보강.
- `ui/dashboard.py`: 사이드바 또는 `thought` 패널 하단에 `Collaboration Matrix` 시각화 컴포넌트 추가.
- `agents/analyst/base.py`: 협업 데이터를 분석하여 비효율적인 연결 고리를 찾는 지능 로직 추가.

### Do NOT
- 외부 그래픽 라이브러리 없이 Rich의 `Table` 및 색상 팔레트만 활용하여 구현.

## Expected Outputs
- `core/observer.py` (Collaboration Tracking)
- `ui/dashboard.py` (Heatmap Rendering)
- `tests/test_collaboration_viz.py` (New)

## Completion Criteria
- Coder가 Analyst에게 리뷰를 맡길 때, 두 에이전트 사이의 연결 강도(Score)가 대시보드 매트릭스에 즉각 반영되어야 함.
- 협업 횟수가 많을수록 히트맵의 색상이 더 진하게(예: Blue -> Cyan -> White) 표시되어야 함.
- `docs/sessions/session_0110.md` 기록.