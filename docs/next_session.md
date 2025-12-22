# Next Session

## Session Goal
- **Swarm Intelligence: Debate Logic Refinement**: `SwarmAgent`의 다중 에이전트 토론(Debate) 로직을 고도화하여, 페르소나 간의 대립과 합의 과정을 구조적으로 처리하고 기록한다.

## Context
- 현재 `SwarmAgent`는 기본적인 토론 흉내를 내고 있지만, 페르소나 간의 명확한 '입장 차이'가 흐릿하고 합의 과정이 단순함.
- `Innovation`(혁신) vs `Stability`(안정)의 대립 구도를 강화하여, 위험한 변경 사항(Evolution)에 대한 견제 장치를 마련해야 함.

## Scope
### Do
- `agents/swarm.py`: `conduct_debate` 메서드를 리팩토링하여 라운드(Round) 기반 토론 로직 구현.
- `agents/swarm.py`: 토론 결과를 `consensus.json` 형태로 요약 저장하는 `synthesize_consensus` 메서드 고도화.
- `docs/prompts/core_agents.yaml`: 토론 전용 시스템 프롬프트(Debate Persona Prompts) 추가/분리.

### Do NOT
- 새로운 에이전트를 추가하지 않음 (기존 Swarm 내 로직 개선).

## Expected Outputs
- `agents/swarm.py` (Refactored)
- `docs/prompts/core_agents.yaml` (Updated)

## Completion Criteria
- `SwarmAgent` 실행 시, 최소 2회 이상의 발언 교환(Round-trip)이 로그에 남아야 함.
- 최종 결과가 `logs/debates/consensus_{TIMESTAMP}.json`에 저장되어야 함.
- `docs/sessions/session_0082.md` 기록.