# Next Session

## Session Goal
- **Dynamic Skill Tree & Role Specialization**: 에이전트별 작업 성공 이력과 평판(`agent_economy`)을 기반으로 특정 도메인(Coding, UI/UX, Research, Security)의 '스킬 포인트'를 자동으로 부여하고, 숙련도에 따라 사용할 수 있는 상위 도구(Advanced Tools)의 잠금을 해제하며, 이를 대시보드에 '기술 트리' 형태로 시각화하는 동적 전문화 시스템을 구축한다.

## Context
- 현재 모든 에이전트는 동일한 도구 셋을 가지거나 하드코딩된 역할에만 의존함.
- 에이전트가 특정 분야에서 반복적인 성과를 거둘 때 그 분야의 전문가로 '성장'하는 재미와 실질적인 성능 이득을 제공해야 함.
- 이는 에이전트 선발(Routing) 시 평판뿐만 아니라 '전문 기술 등급'을 고려하게 만드는 기초 작업임.

## Scope
### Do
- `utils/economy.py`: 작업 범주별 스킬 포인트 산출 로직 `update_skill_points` 추가.
- `core/registry.py`: 스킬 레벨에 따른 도구 사용 권한(Permissions) 필터링 로직 통합.
- `ui/dashboard.py`: 현재 에이전트의 스킬 트리와 전문 분야를 시각화하는 'Skill Radar' 위젯 추가.

### Do NOT
- 실제 에이전트의 LLM 모델 파라미터 튜닝은 배제 (순수 애플리케이션 레벨의 능력 제어).

## Expected Outputs
- `utils/economy.py` (Skill Accumulation)
- `core/registry.py` (Tool Permissions)
- `tests/test_skill_tree.py` (New)

## Completion Criteria
- 코딩 작업을 5회 연속 성공한 에이전트의 'Coding' 스킬 등급이 상승하고, 기존에 잠겨있던 'Apply Patch' 도구의 사용 권한이 해제되어야 함.
- 대시보드 사이드바에 에이전트별 전문성 게이지가 정확히 렌더링되어야 함.
- `docs/sessions/session_0128.md` 기록.