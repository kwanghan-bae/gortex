# Next Session

## Session Goal
- **Debate Memory Integration**: Swarm 토론을 통해 도출된 고비용/고가치 합의안(Consensus)을 `EvolutionaryMemory`에 영구적인 '초월적 규칙(Super Rule)'으로 저장하여, 동일한 문제 발생 시 토론 비용을 절감하고 시스템의 지능을 비약적으로 향상시킨다.

## Context
- 현재 Swarm 토론 결과는 해당 세션의 문제 해결에만 쓰이고 휘발됨.
- 전문가들이 모여 합의한 내용은 시스템의 '헌법'과 같은 가치를 지니므로, 이를 일반적인 경험 규칙보다 상위 등급으로 관리해야 함.

## Scope
### Do
- `agents/swarm.py`: 합의 도출(`synthesize_consensus`) 성공 시, `Analyst`에게 요청하여 이를 정규화된 규칙 포맷으로 변환 및 저장.
- `core/evolutionary_memory.py`: `Super Rule` (Severity 5, High Priority) 타입을 지원하고, 일반 규칙보다 우선 적용되도록 조회 로직 수정.
- `agents/manager.py`: 작업 시작 전 `Super Rule` 존재 여부를 먼저 확인하여 Fast-Track 실행 경로 마련.

### Do NOT
- 모든 토론 결과를 저장하지 않음. `is_debug=True`이거나 명시적으로 중요한 결정일 때만 저장.

## Expected Outputs
- `core/evolutionary_memory.py` (Super Rule Logic)
- `agents/swarm.py` (Memory Integration)
- `tests/test_super_rules.py` (New)

## Completion Criteria
- Swarm 토론 후 `experience.json`에 `is_super_rule: true` 속성을 가진 규칙이 생성되어야 함.
- 다음 번 동일 주제(Topic) 발생 시, Manager가 토론을 생략하고 해당 규칙을 즉시 인용해야 함.
- `docs/sessions/session_0131.md` 기록 준비.
