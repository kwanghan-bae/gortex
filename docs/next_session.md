# Next Session

## Session Goal
- 에이전트 간 합의 도출(Synthesis) 알고리즘 고도화 및 데이터 정규화

## Context
- v2.3.0에서 합의 프로토콜의 기초가 마련되었으나, `analyst`가 `swarm`의 개별 시나리오 원본 데이터를 직접 참조하지 못하고 요약본에 의존하는 한계가 있음.
- `GortexState`에 토론 데이터를 위한 전용 필드를 추가하여 정보 손실 없는 합의가 이루어지도록 개선해야 함.

## Scope
### Do
- `core/state.py`에 `debate_context` 필드(List[Dict]) 추가.
- `agents/swarm.py`에서 각 시나리오의 전체 리포트를 `debate_context`에 보존하도록 수정.
- `agents/analyst.py`가 이 컨텍스트를 직접 읽어 정밀한 트레이드오프 분석을 수행하도록 로직 개선.

### Do NOT
- 기존의 단순 작업 로직에 불필요한 오버헤드 주입 금지.

## Expected Outputs
- `core/state.py`, `agents/swarm.py`, `agents/analyst.py` 수정.

## Completion Criteria
- Analyst가 이전 단계의 모든 시나리오 원본 데이터를 바탕으로 합의안을 작성하는 프로세스가 로그로 확인되어야 함.