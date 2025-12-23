# Next Session

## Session Goal
- **Distributed Conflict Resolution & Consensus Engine**: 파편화된 지식 샤드(Coding, Research, General 등) 간에 발생할 수 있는 상충되는 지침이나 중복된 규칙을 감지하고, 다중 에이전트(Manager, Analyst, Researcher) 간의 토론 및 합의 프로세스를 통해 하나의 정제된 '전역 진리'를 도출하여 지식 베이스를 자율적으로 최적화한다.

## Context
- 현재 Gortex v3.0은 지식을 샤딩하여 관리하지만, 서로 다른 샤드에서 유사한 패턴에 대해 상반된 지침을 내릴 위험이 있음.
- 단순한 규칙 병합을 넘어, 왜 상충이 발생했는지 분석하고 어떤 지침이 더 '현대적'이고 '안전'한지 에이전트들이 토론하여 결정해야 함.
- 이는 분산된 지능들이 하나의 일관된 사고 체계를 유지하게 만드는 핵심 엔진임.

## Scope
### Do
- `core/evolutionary_memory.py`: 샤드 간 트리거 패턴 중첩 및 지침 모순을 전수 조사하는 `detect_global_conflicts` 로직 추가.
- `agents/analyst/base.py`: 상충된 규칙들을 분석하여 토론 의제를 설정하고 합의안을 작성하는 `synthesize_consensus` 기능 강화.
- `agents/swarm.py`: 다중 관점(Innovation vs Stability)에서 규칙의 타당성을 논쟁하는 토론 루프 안착.

### Do NOT
- 실제 데이터베이스 트랜잭션 수준의 정합성 보장이 아닌, LLM의 시맨틱 정합성에 집중함.

## Expected Outputs
- `core/evolutionary_memory.py` (Conflict Detector)
- `agents/swarm.py` (Consensus Loop)
- `tests/test_conflict_resolution.py` (New)

## Completion Criteria
- 두 개의 샤드에 상충되는 규칙(예: '함수명은 Snake case로 하라' vs '함수명은 Camel case로 하라')이 존재할 때, 시스템이 이를 감지하고 하나로 통합해야 함.
- 통합된 규칙은 부모 규칙들의 계보(`parent_rules`)를 유지해야 함.
- `docs/sessions/session_0126.md` 기록.