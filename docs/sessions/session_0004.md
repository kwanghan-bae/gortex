# Session 0004

## Goal
- 에이전트 간 가상 토론 과정 시각화 (Debate Monitor v1)

## What Was Done
- **ui/dashboard.py 수정**: 토론 데이터 보관을 위한 `active_debate` 필드 추가 및 `update_debate_monitor` 메서드 구현. 터미널 UI에 토론 내용을 대조하여 표시하는 레이아웃 반영.
- **main.py 수정**: 에이전트 루프에서 `debate_context`를 감지하여 실시간으로 UI를 업데이트하도록 연동.
- **Web Broadcast 확장**: 웹 대시보드로 전송되는 상태 데이터에 토론 데이터를 포함시킴.

## Decisions
- 토론 모드 시 터미널 메인 화면을 일시적으로 토론 전용 패널로 교체하여 사용자 가시성을 극대화함.
- `Innovation` 페르소나는 Magenta, `Stability` 페르소나는 Cyan 색상으로 구분하여 직관성을 높임.

## Problems / Blockers
- 현재 토론 내용이 길어질 경우 터미널 화면 제약으로 인해 일부 내용이 잘릴 수 있음. 향후 페이징이나 스크롤 지원 검토 필요.

## Notes for Next Session
- 합의 프로토콜의 성능을 평가하기 위해 실제 복잡한 리팩토링 작업을 수행하고, 토론이 결론에 미치는 영향을 분석해야 함.
