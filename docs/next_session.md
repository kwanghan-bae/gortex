# Next Session

## Session Goal
- **Automated Agent Generation Loop**: 시스템이 자신의 능력 밖의 과제(예: 특정 라이브러리 전문 지식 필요)를 감지하면, `Analyst`와 `Coder`가 협력하여 해당 작업에 특화된 새로운 에이전트 클래스를 스스로 설계/작성하고 `AgentRegistry`에 자동으로 등록하는 '지능 증식' 메커니즘을 구축한다.

## Context
- v3.0의 플러그인 구조가 완성됨에 따라 에이전트 추가가 매우 간소화됨.
- 이제는 사람이 에이전트를 만들어주는 것이 아니라, 시스템이 자신의 결핍을 인지하고 스스로 새로운 '전문가'를 채용(생성)할 수 있어야 함.
- 이는 진정한 의미의 자율 진화(Self-Evolution)의 정점임.

## Scope
### Do
- `agents/analyst/base.py`: 새로운 에이전트 필요성을 판단하는 `identify_capability_gap` 메서드 추가.
- `agents/coder.py`: `BaseAgent` 템플릿을 기반으로 에이전트 소스 코드를 생성하는 `generate_new_agent` 로직 보강.
- `core/registry.py`: 런타임에 소스 파일로부터 에이전트를 동적으로 로드하는 `load_agent_from_file` 기능 구현.

### Do NOT
- 실제 그래프 노드 구성을 런타임에 변경하는 복잡한 작업은 다음 단계로 (우선 레지스트리 등록에 집중).

## Expected Outputs
- `agents/analyst/base.py` (Gap Analysis)
- `core/registry.py` (Dynamic Loader)
- `tests/test_agent_generation.py` (New)

## Completion Criteria
- 특정 과제 수행 실패 로그가 쌓였을 때, Analyst가 새로운 에이전트 명세를 제안해야 함.
- 제안된 명세를 바탕으로 생성된 파일이 레지스트리에 에러 없이 등록되어야 함.
- `docs/sessions/session_0105.md` 기록.
