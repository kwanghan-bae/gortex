# Next Session

## Session Goal
- **Predictive Performance Guardrails**: 에이전트가 고부하 작업(예: 대규모 리팩토링, 광범위한 웹 검색)을 수행하기 전, 과거 데이터를 기반으로 예상 토큰 사용량과 실행 시간을 예측하고, 임계치 초과가 예상될 경우 사용자에게 경고하거나 스스로 계획을 최적화하는 '선제적 방어선'을 구축한다.

## Context
- 현재 시스템은 작업을 일단 실행한 뒤에 비용과 효율을 측정함.
- 복잡도가 높은 작업의 경우 실행 중간에 API 할당량이 소진되거나 에너지가 바닥나 작업이 중단되는 리스크가 있음.
- `EfficiencyMonitor`의 누적 데이터를 활용하여 '실행 전 예측' 지능을 강화함.

## Scope
### Do
- `utils/efficiency_monitor.py`: 작업 유형별 평균 토큰/시간 데이터를 기반으로 한 `predict_resource_usage` 메서드 추가.
- `agents/planner.py`: 계획 수립 직후 각 단계의 예상 비용을 산출하고, 총합이 위험 수준일 때 `thought_process`에 경고 주입.
- `ui/dashboard.py`: 예측된 비용을 대시보드 상단에 '예상 비용'으로 미리 표시.

### Do NOT
- 복잡한 머신러닝 모델 도입은 배제 (통계적 가중치 평균 방식 우선).

## Expected Outputs
- `utils/efficiency_monitor.py` (Update)
- `agents/planner.py` (Predictive mode)
- `tests/test_performance_prediction.py` (New)

## Completion Criteria
- 특정 작업에 대해 과거 평균보다 2배 이상의 리소스가 필요할 것으로 예측될 때, 플래너가 "Resource Alert"를 발생시켜야 함.
- 대시보드에 현재 작업의 '예상 완료 시간'이 실시간으로 노출되어야 함.
- `docs/sessions/session_0108.md` 기록.