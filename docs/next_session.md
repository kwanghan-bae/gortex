# Next Session

## Session Goal
- 합의 결과 사후 평가 및 페르소나 가중치 학습 (Consensus Learner v1)

## Context
- 토론 시스템이 완성되었으나, 모든 결정이 항상 최선은 아닐 수 있음.
- 합의된 안을 실행한 후의 효율성 점수(`efficiency_score`)를 추적하여, 특정 상황에서 어떤 관점(Innovation vs Stability)이 더 성공적이었는지 기록해야 함.

## Scope
### Do
- `core/state.py`에 `consensus_history` 필드 추가 (합의안 및 사후 점수 기록).
- `agents/analyst.py`에서 이전 합의안의 실행 결과를 평가하여 '교훈(Lesson)'을 추출하는 로직 추가.
- 추출된 교훈을 `EvolutionaryMemory`에 저장하여 향후 합의 시 가중치로 활용.

### Do NOT
- 복잡한 머신러닝 알고리즘 도입 금지 (단순한 점수 기반 통계 활용).

## Expected Outputs
- `core/state.py`, `agents/analyst.py`, `core/evolutionary_memory.py` 수정.

## Completion Criteria
- 합의안 실행 후의 효율성 점수가 합의 이력에 정상 기록되고, Analyst가 이를 분석하는 과정이 확인되어야 함.