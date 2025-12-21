# Next Session

## Session Goal
- 에이전트 간 가상 토론 과정 시각화 (Debate Monitor v1)

## Context
- 합의 프로토콜이 데이터 레벨에서 완성되었으나, 사용자 입장에서는 블랙박스 내에서 결과만 통보받는 느낌을 줄 수 있음.
- `Swarm`에서의 관점 충돌과 `Analyst`의 종합 과정을 시각적 데이터로 변환하여 대시보드에 노출해야 함.

## Scope
### Do
- `ui/dashboard.py`에 토론 현황을 표시할 수 있는 `update_debate_monitor` 메서드 추가.
- `main.py`에서 `debate_context` 데이터를 UI 및 웹 서버로 실시간 스트리밍하도록 연동.
- 웹 대시보드에서 상반된 페르소나의 의견을 대조하여 보여주는 데이터 스키마 확장.

### Do NOT
- 대시보드 레이아웃을 지나치게 복잡하게 만들지 말 것 (기존 패널 재활용 고려).

## Expected Outputs
- `ui/dashboard.py`, `main.py` 수정.

## Completion Criteria
- 터미널 또는 웹 대시보드에서 'Innovation'과 'Stability'의 상반된 리포트가 대조되어 표시되는 것이 확인되어야 함.
