# Next Session

## Session Goal
- **Collaborative Multi-Agent Debugging**: 단일 에이전트(Coder)가 해결하지 못한 고난도 버그에 대해 `Swarm` 노드와 `Analyst`가 협력하여 공동 진단하고, 여러 가설을 동시에 검증하여 최적의 패치를 도출하는 '집단 지성 수리 루프'를 강화한다.

## Context
- 현재 수리는 주로 `Analyst` 진단 -> `Coder` 집도로 이루어짐.
- 하지만 원인이 불분명한 간헐적 버그나 복잡한 의존성 문제는 단일 관점으로 해결이 어려움.
- `Swarm`의 '토론' 지능을 디버깅에 도입하여, 다양한 해결책을 제안받고 상호 비판을 통해 신뢰도를 높여야 함.

## Scope
### Do
- `agents/swarm.py`: 'Debug Mode' 추가. 에러 로그를 바탕으로 여러 페르소나가 각자 다른 가설을 제안하도록 유도.
- `agents/analyst/base.py`: Swarm이 제안한 여러 패치 후보 중 가장 안전하고 효율적인 것을 선별하는 `synthesize_debug_consensus` 구현.
- `core/graph.py`: Coder가 반복 실패 시 자동으로 'Swarm Debug Mode'로 라우팅하는 엣지 보강.

### Do NOT
- 인프라 수준의 디버깅(Docker, OS Kernel 등)은 범위에서 제외.

## Expected Outputs
- `agents/swarm.py` (Debug Persona support)
- `agents/analyst/base.py` (Debug Synthesis)
- `tests/test_swarm_debugging.py` (New)

## Completion Criteria
- Coder가 3회 이상 동일 버그 수리에 실패했을 때, Swarm이 개입하여 최소 2개 이상의 대안적 가설을 제시해야 함.
- 최종적으로 선택된 가설이 기존의 실패한 방식과 달라야 함.
- `docs/sessions/session_0107.md` 기록.
