# Next Session

## Session Goal
- **Proactive Dependency Visualization & Impact Mapping**: 리팩토링이나 핵심 모듈 수정 전, 해당 변경이 시스템 전체에 미치는 영향(Side Effect)을 사전에 시뮬레이션하고, 이를 트리(Tree) 또는 그래프(Graph) 형식으로 시각화하여 위험도를 리포트하는 '영향력 지도 엔진'을 구축한다.

## Context
- 현재 Gortex는 Planner가 영향력을 분석하긴 하지만, 정성적인 판단에 의존하며 시각적 근거가 부족함.
- `SynapticIndexer`를 활용하여 실제 코드 레벨의 의존성(Call Graph)을 추출하고, 변경 대상과 연결된 모든 모듈을 명시적으로 식별해야 함.
- 이는 대규모 리팩토링의 안전성을 보장하는 핵심 지능임.

## Scope
### Do
- `utils/indexer.py`: 특정 심볼(Function/Class) 변경 시 영향을 받는 '상향 의존성(Reverse Dependencies)' 추적 로직 추가.
- `agents/analyst/base.py`: 추출된 데이터를 바탕으로 Mermaid 다이어그램을 생성하는 `generate_impact_map` 메서드 구현.
- `ui/dashboard.py`: 영향력 지도를 대시보드 하단에 렌더링하는 시각화 위젯 추가.

### Do NOT
- 실제 런타임 추적(Dynamic Analysis)은 배제하고 정적 코드 분석(Static Analysis)에 집중.

## Expected Outputs
- `utils/indexer.py` (Reverse Dependency Tracker)
- `agents/analyst/base.py` (Impact Map Generator)
- `tests/test_dependency_viz.py` (New)

## Completion Criteria
- 특정 함수 이름을 입력했을 때, 그 함수를 참조하는 모든 파일과 라인 번호를 정확히 식별해야 함.
- 시각화 결과물(Mermaid)이 문법적으로 올바르게 생성되어야 함.
- `docs/sessions/session_0121.md` 기록.
