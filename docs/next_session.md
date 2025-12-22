# Next Session

## Session Goal
- **Real-time System Energy Visualizer**: 대시보드 레이아웃을 조정하여, 시스템의 현재 에너지 상태와 충전율을 시각적으로 강조하는 전용 패널을 중앙 상단에 배치하고, 실시간 애니메이션(Progress Bar Pulse)을 통해 시스템의 활력도를 직관적으로 전달한다.

## Context
- `Session 0095`에서 에너지 회복 루프를 구축했으나, 현재는 사이드바의 텍스트와 작은 아이콘으로만 표시되어 시인성이 낮음.
- Gortex v3.0의 '살아있는 시스템' 컨셉을 강화하기 위해, 에너지 상태를 시스템의 가장 핵심적인 지표로 시각적 격상시킴.

## Scope
### Do
- `ui/dashboard.py`: `create_layout` 수정. 중앙 상단에 `header` 또는 `energy` 전용 수평 패널 공간 확보.
- `ui/dashboard.py`: `update_energy_visualizer` 메서드 추가. 현재 에너지에 따라 색상이 변하는(Green -> Yellow -> Red) 대형 게이지 구현.
- `main.py`: 에너지 회복 루프와 대시보드 전용 패널의 실시간 동기화 강화.

### Do NOT
- 대화창(`main`)의 가독성을 해칠 정도로 거대한 그래픽은 지양 (터미널의 깔끔함 유지).

## Expected Outputs
- `ui/dashboard.py` (Layout & Gauge Refinement)
- `main.py` (Visual Trigger integration)
- `tests/test_energy_ui.py` (New)

## Completion Criteria
- 시스템 상단에 현재 에너지를 보여주는 게이지 패널이 실시간으로 렌더링되어야 함.
- 에너지가 10% 미만일 때 게이지가 빨간색으로 깜빡이며 유지보수 모드임을 시각적으로 강력히 경고해야 함.
- `docs/sessions/session_0109.md` 기록.
