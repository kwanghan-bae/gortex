# Next Session

## Session Goal
- **Dynamic Agent Orchestration & Capability Discovery**: `Manager`가 하드코딩된 에이전트 목록이 아닌, `AgentRegistry`를 실시간 조회하여 사용자 요청(또는 작업 단계)을 처리하기 위해 가장 적합한 도구와 역할을 가진 에이전트를 자율적으로 탐색하고 선택하는 로직을 구현한다.

## Context
- 102세션을 통해 핵심 에이전트들이 레지스트리에 등록됨.
- 현재 `Manager`는 여전히 "다음은 coder야"라고 하드코딩된 이름을 리턴하고 있음.
- v3.0의 진정한 가치는 "이 작업에는 A 도구가 필요한데, 누가 쓸 줄 알아?"라고 물으면 레지스트리가 "Planner가 그 도구를 갖고 있어"라고 대답해주는 동적 매칭에 있음.

## Scope
### Do
- `core/registry.py`: `get_agents_by_role(role)` 및 `get_agents_by_tool(tool)` 유틸리티 메서드 추가.
- `agents/manager.py`: 의도 분석 결과 도출 시, 필요한 '능력(Capability)'을 추출하고 레지스트리에서 에이전트를 조회하여 `next_node`를 결정하는 로직 도입.
- `agents/manager.py`: 여러 후보 에이전트가 있을 경우 평판 점수(`agent_economy`)가 가장 높은 에이전트를 우선 선택.

### Do NOT
- 모든 라우팅을 한 번에 동적화하지 않음 (단계적 전환).

## Expected Outputs
- `core/registry.py` (Extended)
- `agents/manager.py` (Refined with discovery logic)
- `tests/test_dynamic_orchestration.py` (New)

## Completion Criteria
- 새로운 에이전트(예: `CloudDeployer`)를 레지스트리에 등록만 해도, `Manager`가 관련 요청 시 해당 에이전트를 `next_node`로 지목해야 함.
- `docs/sessions/session_0103.md` 기록.
