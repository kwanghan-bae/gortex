# Next Session

## Session Goal
- **Real-time Reputation Dashboard**: 에이전트별 평판 등급, 포인트, 성과 통계를 TUI 대시보드에 시각화하여 시스템의 내부 상태를 직관적으로 파악할 수 있게 한다.

## Context
- `Session 0088`에서 경제 시스템 백엔드를 구축함.
- 현재 사용자는 평판 변화를 로그로만 확인할 수 있어 가독성이 낮음.
- '신뢰할 수 있는 시스템'을 위해 에이전트들이 서로를 어떻게 평가하는지 투명하게 공개해야 함.

## Scope
### Do
- `ui/dashboard.py`: `update_sidebar` 메서드 확장하여 에이전트 경제 정보 렌더링 추가.
- `ui/dashboard.py`: 포인트 순위를 보여주는 소형 테이블(`Reputation Leaderboard`) 레이아웃 추가.
- `main.py`: 루프 종료 시마다 대시보드에 경제 상태 업데이트 트리거 연동.

### Do NOT
- 복잡한 차트나 외부 라이브러리 추가를 지양하고 Rich 기본 기능을 최대한 활용.

## Expected Outputs
- `ui/dashboard.py` (Update)
- `tests/test_dashboard_economy.py` (New)

## Completion Criteria
- `/status` 명령이나 사이드바에서 Coder의 `Silver` 등급과 포인트가 실시간으로 표시되어야 함.
- `docs/sessions/session_0089.md` 기록.
