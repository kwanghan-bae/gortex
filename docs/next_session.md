# Next Session

## Session Goal
- 다중 에이전트 합의(토론) 프로토콜(Multi-Agent Consensus Protocol) 구현

## Context
- 시스템이 복잡해짐에 따라 단일 에이전트의 판단보다는 여러 관점(안정성 vs 혁신성)에서의 토론이 필요함.
- `Swarm` 노드를 확장하여 비판적 검토 과정을 시뮬레이션하고 최종 합의안을 도출해야 함.

## Scope
### Do
- `agents/swarm.py`에서 상반된 페르소나를 가진 시나리오 생성 로직 추가.
- `agents/analyst.py`에 토론 결과 종합(`synthesize_consensus`) 메서드 추가.
- `agents/manager.py`에서 고위험 작업 시 토론 워크플로우 트리거 로직 추가.

### Do NOT
- 기존의 단일 작업 처리 로직 파괴 금지 (필요 시에만 토론 트리거).

## Expected Outputs
- `agents/swarm.py`, `agents/analyst.py`, `agents/manager.py` 수정.

## Completion Criteria
- 위험도가 높은 요청에 대해 최소 2개 이상의 상반된 의견이 제시되고, Analyst가 이를 종합하여 결론을 내리는 프로세스가 확인되어야 함.
