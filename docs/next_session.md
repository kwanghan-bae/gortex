# Next Session

## Session Goal
- **Energy Recovery & Maintenance Mode**: 시스템 에너지가 낮을 때 스스로 휴식하며 자원을 회복하는 '유지보수 모드'를 도입하고, 아이들(Idle) 시간 동안 에너지가 점진적으로 충전되는 메커니즘을 구현한다.

## Context
- `Session 0087`에서 저에너지 시 작업 가지치기 기능을 추가함.
- 현재는 에너지가 줄어들기만 하고 다시 채워지는 로직이 없어, 결국 시스템이 멈추게 됨.
- 생물학적 시스템처럼 휴식을 통한 '에너지 충전' 개념을 도입하여 시스템의 영속성을 확보해야 함.

## Scope
### Do
- `core/engine.py`: 에너지가 일정 수준 이하(예: 10%)로 떨어지면 강제로 `Maintenance Mode`로 진입하는 로직 추가.
- `main.py`: 사용자의 입력이 없는 Idle 시간 동안 에너지를 초당 일정량(예: 0.1) 회복하는 비동기 루틴 구현.
- `ui/dashboard.py`: 에너지 회복 중임을 나타내는 시각적 효과(Pulse 등) 추가.

### Do NOT
- 외부 전력 관리나 실제 PC 절전 모드와 연동하지 않음 (순수 시스템 가상 에너지).

## Expected Outputs
- `main.py` (Update with recovery loop)
- `ui/dashboard.py` (Update)
- `tests/test_energy_recovery.py` (New)

## Completion Criteria
- 시스템을 실행해두고 1분간 대기했을 때, 에너지가 최소 5포인트 이상 상승해야 함.
- 에너지가 10 미만일 때 에이전트 작업 요청 시 "휴식 중" 메시지가 출력되어야 함.
- `docs/sessions/session_0095.md` 기록.
