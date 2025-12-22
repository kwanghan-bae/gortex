# Next Session

## Session Goal
- **Gortex v3.0 Architecture Design: Decoupled Agent Registry**: 100회의 경험을 바탕으로, 현재의 하드코딩된 에이전트 구조를 탈피하여 에이전트를 독립적인 플러그인처럼 등록하고 관리할 수 있는 '중앙 레지스트리' 중심의 v3.0 아키텍처를 설계하고 기초를 구현한다.

## Context
- 현재 새로운 에이전트를 추가하려면 `graph.py`와 여러 유틸리티를 수정해야 함.
- 확장이 용이한 시스템을 위해, 에이전트가 자신의 명세(Persona, Tools, Capacity)를 레지스트리에 등록하면 `Manager`가 이를 자율적으로 탐색하여 활용하는 구조가 필요함.
- 이는 Gortex의 '모듈형 진화'를 위한 필수 단계임.

## Scope
### Do
- `core/registry.py` (New): `AgentRegistry` 클래스 구현.
- `agents/base.py` (Update): 모든 에이전트의 공통 인터페이스 및 자기 기술(Self-Description) 기능 추가.
- `docs/TECHNICAL_SPEC.md`: v3.0 아키텍처 청사진(Blueprints) 업데이트.

### Do NOT
- 기존의 작동하는 그래프를 즉시 파괴하지 않음 (병행 운영 및 점진적 마이그레이션).

## Expected Outputs
- `core/registry.py` (New)
- `agents/base.py` (Refined)
- `docs/TECHNICAL_SPEC.md` (Updated)

## Completion Criteria
- 에이전트 클래스를 작성하고 레지스트리에 등록했을 때, 해당 에이전트의 메타데이터를 레지스트리에서 조회할 수 있어야 함.
- `docs/sessions/session_0101.md` 기록.
