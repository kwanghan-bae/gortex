# Next Session

## Session Goal
- 에이전트 간 상호 평가 및 자원 할당 경제 시스템 고도화 (Peer Review Economy v1)

## Context
- v2.2.14에서 도입된 평판 기반 모델 할당이 현재는 단순한 레벨 체계에 머물러 있음.
- 에이전트가 `analyst`로부터 좋은 리뷰를 받거나 다른 에이전트의 작업을 도왔을 때 실시간으로 '토큰 크레딧'을 획득하고, 이를 사용하여 더 비싼 모델을 '구매'하는 역동적인 경제 모델이 필요함.

## Scope
### Do
- `core/state.py`에 에이전트별 `token_credits` 필드 추가.
- `agents/analyst.py`의 `cross_validate` 결과에 따라 보상(Credit)을 차등 지급하는 로직 강화.
- `agents/manager.py`에서 에이전트가 보유한 크레딧에 따라 모델 티어를 결정하는 경제 기반 스케줄링 구현.

### Do NOT
- 실제 비용(USD)과 연동하지 말 것 (철저히 시스템 내부 가상 포인트).

## Expected Outputs
- `core/state.py`, `agents/analyst.py`, `agents/manager.py` 수정.

## Completion Criteria
- Analyst의 승인을 받은 Coder가 크레딧을 획득하고, 다음 작업에서 더 높은 티어의 모델을 할당받는 과정이 확인되어야 함.
