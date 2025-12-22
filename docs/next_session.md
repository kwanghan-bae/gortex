# Next Session

## Session Goal
- **Cross-Agent Reputation System**: 에이전트(`Coder`, `Researcher` 등)의 작업 결과물을 다른 에이전트(`Analyst`)가 평가하여 평판 점수(`agent_economy`)를 갱신하고, 고평판 에이전트에게 더 많은 리소스를 할당하는 선순환 시스템을 구축한다.

## Context
- 현재 `agent_economy`는 구조만 있고 실제 작동 로직이 약함.
- 작업의 질에 따른 차등 보상이 없으므로 에이전트들이 대충 답변할 가능성(Laziness)이 존재함.
- '평판'을 통해 고성능 모델(Pro) 사용권을 획득하는 등의 게임화 요소를 강화함.

## Scope
### Do
- `agents/analyst/reflection.py`: 작업 품질 평가(`evaluate_work_quality`) 메서드 추가.
- `utils/economy.py` (New): 포인트 지급 및 평판 관리 전문 유틸리티 신설.
- `core/state.py`: `GortexState` 내 `agent_economy` 데이터 구조 최적화.

### Do NOT
- 실제 암호화폐나 외부 결제 시스템은 도입하지 않음 (순수 내부 가상 경제).

## Expected Outputs
- `utils/economy.py` (New)
- `agents/analyst/reflection.py` (Update)
- `tests/test_agent_economy.py` (New)

## Completion Criteria
- Coder가 작업을 완수했을 때, Analyst의 평가에 따라 `agent_economy`의 포인트가 정상적으로 가감되는지 확인.
- `docs/sessions/session_0088.md` 기록.