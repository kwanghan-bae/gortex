# Next Session

## Session Goal
- **Autonomous Task Prioritization**: 시스템 리소스(에너지, 토큰 예산) 상황에 따라 플래너가 수립한 작업의 우선순위를 동적으로 평가하고, 저가치 작업을 자동으로 연기하거나 생략하는 의사결정 지능을 구현한다.

## Context
- 현재 플래너는 모든 작업을 동일한 비중으로 처리하려 함.
- 에너지가 낮거나 API 비용이 임계치에 도달했을 때, 핵심 기능 구현에만 집중하고 '문서 정리'나 '부가 기능'은 뒤로 미룰 수 있어야 함.
- 에이전트 경제 시스템(`agent_economy`)과의 연동이 필요함.

## Scope
### Do
- `agents/planner.py`: 작업별 '가치 점수(Value Score)' 부여 로직 추가.
- `agents/manager.py`: 현재 리소스 상태를 기반으로 플랜을 재구성(Pruning Tasks)하는 필터링 로직 구현.
- `core/state.py`: `GortexState`에 작업 우선순위 관련 메타데이터 필드 추가 고려.

### Do NOT
- 사용자의 명시적 요청 작업은 절대 생략하지 않음 (자동 생성된 부가 작업만 대상).

## Expected Outputs
- `agents/planner.py` (Update)
- `agents/manager.py` (Update)
- `tests/test_task_prioritization.py` (New)

## Completion Criteria
- 에너지가 20 이하일 때, '문서 생성' 작업이 플랜에서 자동으로 제외되는지 검증.
- `docs/sessions/session_0087.md` 기록.
