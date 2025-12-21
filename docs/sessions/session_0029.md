# Session 0029

## Goal
- 에이전트 프롬프트 외부 템플릿화 및 동적 관리 (Dynamic Prompting v1)

## What Was Done
- **docs/prompts/ 디렉토리 생성**: 각 에이전트별 시스템 지침을 YAML 형식으로 관리하기 위한 기반 마련. `core_agents.yaml` 작성.
- **utils/prompt_loader.py 구현**: 외부 YAML 파일을 로드하고 런타임 변수 치환(`.format()`) 기능을 제공하는 싱글톤 로더 구축.
- **agents/manager.py 수정**: 수백 라인의 하드코딩된 프롬프트 문자열을 제거하고 `PromptLoader`를 통해 동적으로 주입하도록 개편.

## Decisions
- 프롬프트 관리는 코드 수정 없이 지능을 튜닝할 수 있는 핵심 인프라이므로, 최상위 `docs/` 하위에서 관리하기로 함.
- 치환 변수 누락 시의 안정성을 위해 `try-except` 폴백 로직을 로더에 포함함.

## Problems / Blockers
- 현재 `manager.py`만 개편 완료됨. `Planner`, `Coder`, `Researcher`, `Analyst` 등 나머지 에이전트들에 대해서도 순차적인 프롬프트 이전 작업이 필요함.

## Notes for Next Session
- 나머지 에이전트들의 프롬프트를 `core_agents.yaml`로 이전하고, 각 에이전트 노드에서 `PromptLoader`를 사용하도록 일괄 수정해야 함.
