# Next Session

## Session Goal
- **Intelligent Task Prioritization & Preemptive Scheduling**: 작업 대기열(Task Queue)에 쌓인 수많은 단계들을 긴급도(Urgency)와 시스템 임팩트(Impact)를 기준으로 자동 분류하고, 고가치 작업을 가장 먼저 실행하며 리소스 여유 시 백그라운드 작업을 배치하는 '전략적 작업 스케줄러'를 구축한다.

## Context
- 현재 작업은 Planner가 생성한 순서대로만 실행됨.
- 하지만 보안 패치, 치명적 버그 수정 등은 코드 가독성 개선보다 먼저 처리되어야 함.
- 또한, 리소스가 남을 때 수행하면 좋은 '정적 분석'이나 '문서화' 등의 작업을 후순위로 미뤄두었다가 처리하는 영리함이 필요함.

## Scope
### Do
- `core/engine.py`: 작업 우선순위를 계산하고 재배열하는 `PriorityScheduler` 로직 추가.
- `core/state.py`: 개별 작업 단계(Plan Step)에 `priority_score` 및 `category` 메타데이터 포함.
- `agents/planner.py`: 계획 수립 시 각 단계의 가중치를 계산하여 출력하는 기능 강화.

### Do NOT
- 실제 운영체제의 프로세스 우선순위(Nice 등) 변경은 배제 (AI 애플리케이션 레벨의 스케줄링).

## Expected Outputs
- `core/engine.py` (Priority Scheduler)
- `agents/planner.py` (Priority-Aware Planning)
- `tests/test_task_prioritization.py` (New)

## Completion Criteria
- 계획된 작업 중 'Security' 또는 'Critical Fix' 범주가 포함된 경우, 기존 순서와 상관없이 최상단으로 배치되어야 함.
- 저부하 상태일 때만 'Documentation' 범주의 작업을 실행하는지 확인.
- `docs/sessions/session_0120.md` 기록.