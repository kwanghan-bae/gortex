# Next Session

## Session Goal
- **Proactive Tech Scout & Capability Expansion**: 시스템의 미비한 기능이나 외부의 새로운 기술 트렌드를 감지하여, 시스템에 필요한 새로운 '전문가 에이전트'의 명세를 스스로 설계하고, 해당 에이전트의 코드를 자동 생성 및 중앙 레지스트리에 등록하여 시스템의 능력을 자율적으로 확장한다.

## Context
- 현재 Gortex는 이미 Milestone 3.0을 달성하여 기본 에이전트들을 갖추고 있음.
- 하지만 특정 도메인(예: 이미지 생성, 보안 감사 강화 등)에 특화된 전문가가 부족할 경우, 에러 발생 후 대응하는 것이 아니라 선제적으로 '팀원'을 뽑아 교육(코드 생성)해야 함.
- 이는 Gortex가 단순한 '도구'를 넘어 스스로 진화하는 '조직'으로 성장하는 핵심 단계임.

## Scope
### Do
- `agents/trend_scout.py`: 현재 코드베이스와 외부(또는 모의) 기술 트렌드를 비교하여 '필요한 전문가'를 제안하는 `scout_needed_capabilities` 로직 추가.
- `agents/coder.py`: 제안된 명세를 바탕으로 `BaseAgent`를 상속받는 새로운 에이전트 소스 코드를 생성하는 `spawn_new_agent` 기능 강화.
- `core/registry.py`: 새롭게 생성된 에이전트 파일을 런타임에 동적으로 로드하고 노드로 추가하는 `dynamic_node_injection` 구현.

### Do NOT
- 외부 실시간 웹 크롤링은 배제하고(Researcher 활용 가능), 사전에 정의된 '기술 레이더' 또는 현재 시스템의 에러 패턴을 기술 트렌드로 의인화하여 처리함.

## Expected Outputs
- `agents/trend_scout.py` (Capability Scouter)
- `agents/auto_spawned_*.py` (Generated Agent)
- `tests/test_agent_generation.py` (New)

## Completion Criteria
- 새로운 전문가(예: `SecurityAuditorAgent`)가 필요하다고 판단되었을 때, 1분 이내에 해당 파일이 생성되고 `AgentRegistry`에 공식 등록되어야 함.
- 등록된 에이전트가 `GortexState`를 인자로 받아 `run` 메서드를 실행할 수 있어야 함.
- `docs/sessions/session_0125.md` 기록.
