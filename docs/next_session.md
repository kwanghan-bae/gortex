# Next Session

## Session Goal
- **Migration of Core Agents to v3.0 Standard**: `Planner`, `Coder`, `Analyst` 등 핵심 에이전트들을 v3.0 표준인 `BaseAgent` 기반 클래스 구조로 리팩토링하고 `AgentRegistry`에 등록한다.

## Context
- `Session 0101`에서 새로운 아키텍처의 기반(Registry, BaseAgent)을 마련함.
- 이제 실제 에이전트들을 이 구조로 마이그레이션하여, 플러그인 스타일의 에이전트 관리가 실제로 작동함을 증명해야 함.
- 기존의 함수 기반 노드(`planner_node`, `coder_node` 등)는 클래스 인스턴스 호출 방식으로 대체됨.

## Scope
### Do
- `agents/planner.py`: `PlannerAgent(BaseAgent)` 클래스로 리팩토링.
- `agents/coder.py`: `CoderAgent(BaseAgent)` 클래스로 리팩토링.
- `agents/analyst/base.py`: `AnalystAgent`를 `BaseAgent` 상속 구조로 업데이트.
- `core/graph.py`: 레지스트리에서 에이전트를 가져와 워크플로우에 등록하는 방식으로 점진적 전환.

### Do NOT
- 모든 에이전트(Swarm, TrendScout 등)를 한 번에 옮기지 않음 (핵심 3종 우선).

## Expected Outputs
- `agents/planner.py` (Class-based)
- `agents/coder.py` (Class-based)
- `core/graph.py` (Updated registration)
- `tests/test_v3_migration.py` (New)

## Completion Criteria
- 마이그레이션된 에이전트들이 레지스트리에 정상 등록되어야 함.
- 기존의 LangGraph 실행 흐름이 깨지지 않고 동일하게 작동해야 함 (하위 호환성 유지).
- `docs/sessions/session_0102.md` 기록.