# Next Session

## Session Goal
- **Intelligent Resource Scaling & Dynamic Concurrency**: 시스템 부하와 작업 대기열(Task Queue)의 길이를 감지하여, 리소스가 여유로울 때는 에이전트의 병렬 실행(Concurrency)을 강화하고, 과부하 시에는 작업 우선순위에 따라 리소스를 동적으로 제한하는 '지능형 스케일링 엔진'을 구축한다.

## Context
- 현재 Gortex는 모든 작업을 순차적으로 처리하거나 고정된 스레드 풀을 사용함.
- 복잡한 대규모 프로젝트에서는 분석과 코딩이 병렬로 일어나야 효율이 극대화됨.
- 또한, 리소스(메모리/CPU) 상태에 따라 동적으로 동시 실행 수를 조절하여 시스템의 안정성을 보장해야 함.

## Scope
### Do
- `core/engine.py`: 작업 부하를 감지하여 스레드/비동기 풀의 크기를 동적으로 조절하는 `ScalingManager` 통합.
- `utils/resource_monitor.py` (New): 시스템 자원(CPU, Memory) 및 대기열 상태를 실시간 모니터링하는 유틸리티 구현.
- `main.py`: 동적 스케일링을 반영한 비동기 실행 루프 최적화.

### Do NOT
- 외부 클라우드 오토스케일링 연동은 배제 (순수 로컬 프로세스 관리).

## Expected Outputs
- `utils/resource_monitor.py` (New Monitor)
- `core/engine.py` (Scaling Logic)
- `tests/test_budget_scaling.py` (New)

## Completion Criteria
- 시스템 부하가 30% 이하일 때, 동시 작업 가능 수가 최소 2배 이상으로 확장되어야 함.
- 작업 대기열이 10개 이상 쌓일 때, 'Critical' 등급 작업에 리소스를 최우선 배분하는지 확인.
- `docs/sessions/session_0119.md` 기록.
