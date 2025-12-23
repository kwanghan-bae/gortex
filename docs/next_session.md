# Next Session

## Session Goal
- **Distributed Conflict Resolution**: 여러 지식 샤드에 분산된 규칙들이 서로 상충되거나 모순될 경우(예: `coding_shard`와 `general_shard`의 지침 충돌), 이를 자동으로 감지하고 `Analyst`와 `Swarm`이 협력하여 최신 상황에 맞는 단일 지침으로 통합하는 '지능형 갈등 해결' 엔진을 구축한다.

## Context
- 지식이 파편화됨에 따라 각 샤드 간의 일관성을 유지하는 것이 중요해짐.
- 서로 다른 에이전트가 생성한 규칙들이 충돌할 경우, 시스템의 의사결정이 모호해질 리스크가 있음.
- "최신성", "성공률", "권위(Severity)"를 기준으로 규칙의 우선순위를 정립함.

## Scope
### Do
- `core/evolutionary_memory.py`: 샤드 간 모순되는 트리거 패턴을 찾는 `detect_cross_shard_conflicts` 메서드 추가.
- `agents/analyst/base.py`: 감지된 갈등을 해소하기 위해 `Swarm` 토론을 요청하고 결과를 반영하는 `resolve_knowledge_conflict` 로직 구현.
- `experience.json.migrated.bak`: 만약의 사태를 대비한 정기적인 '지식 스냅샷' 기능 보강.

### Do NOT
- 사용자가 수동으로 'Lock'을 걸어둔 규칙은 자동 수정 대상에서 제외.

## Expected Outputs
- `core/evolutionary_memory.py` (Conflict detection)
- `agents/analyst/base.py` (Conflict resolution)
- `tests/test_conflict_resolution.py` (New)

## Completion Criteria
- 서로 다른 샤드에 상충하는 규칙 2개를 주입했을 때, 시스템이 이를 감지하고 하나로 통합하거나 우선순위를 명확히 해야 함.
- `docs/sessions/session_0113.md` 기록.
