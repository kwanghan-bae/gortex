# Next Session

## Session Goal
- **v3.0 Interactive Dashboard Upgrade**: `AgentRegistry`에 등록된 에이전트 목록과 그들이 제공하는 기능(Capabilities)을 TUI 대시보드에 시각화하고, 명령어를 통해 실시간으로 레지스트리 상태를 확인할 수 있도록 고도화한다.

## Context
- v3.0 아키텍처 도입으로 에이전트가 동적으로 관리되기 시작함.
- 현재 대시보드는 하드코딩된 에이전트들만 인지하고 있어, 새롭게 등록된 에이전트(예: `Deployer`)를 보여주지 못함.
- 시스템의 '확장성'을 사용자에게 시각적으로 전달하여 v3.0의 정체성을 강화함.

## Scope
### Do
- `ui/dashboard.py`: 사이드바 하단에 `Registry` 패널을 추가하여 현재 등록된 모든 에이전트와 그들의 역할을 리스트업.
- `ui/dashboard.py`: `update_sidebar`에서 `current_agent`뿐만 아니라 해당 에이전트가 현재 사용 중인 '능력(Capability)'을 강조 표시.
- `core/commands.py`: `/agents` 명령어를 추가하여 레지스트리에 등록된 에이전트들의 상세 메타데이터(버전, 도구 등)를 출력.

### Do NOT
- 대시보드의 전체 레이아웃을 크게 바꾸지 않음 (기존 사이드바 활용).

## Expected Outputs
- `ui/dashboard.py` (Registry Visualization)
- `core/commands.py` (New /agents command)
- `tests/test_dashboard_v3.py` (New)

## Completion Criteria
- 새로운 에이전트를 등록했을 때, 별도의 코드 수정 없이 대시보드 리스트에 즉시 나타나야 함.
- `/agents` 명령 시 모든 등록된 에이전트의 메타데이터가 표(Table) 형식으로 예쁘게 출력되어야 함.
- `docs/sessions/session_0104.md` 기록.