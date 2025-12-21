# Session 0030

## Goal
- 모든 에이전트 지침의 외부 템플릿 통합 (Global Dynamic Prompting v1)

## What Was Done
- **docs/prompts/core_agents.yaml 보강**: `planner`, `coder`, `researcher`, `analyst`의 모든 상세 지침을 통합 관리 파일로 이전.
- **에이전트 파일 전수 개편**:
    - `planner.py`, `coder.py`, `researcher.py`, `analyst.py`에서 하드코딩된 대규모 프롬프트 문자열 제거.
    - `PromptLoader`를 연동하여 런타임에 지능을 동적으로 주입하는 구조로 전환.
- **Bug Fix**: `researcher.py`의 비동기 실행 블록 누락 및 변수 미정의 오류 해결.

## Decisions
- 시스템의 모든 지적 설계를 `docs/prompts/` 하위에 데이터화함으로써, 코드 수정 없이 지시 사항 변경만으로 시스템 성능을 최적화할 수 있는 유연성을 확보함.
- `PromptLoader`의 싱글톤 인스턴스를 통해 리소스 로딩 효율을 극대화함.

## Problems / Blockers
- 현재 모든 템플릿이 단일 YAML 파일(`core_agents.yaml`)에 모여 있어, 에이전트가 많아질 경우 파일이 거대해질 수 있음. 향후 에이전트별 개별 YAML 파일로 분리하는 구조 검토 필요.

## Notes for Next Session
- 시스템의 '물리적 자동화'를 위해, 현재 `pre_commit.sh`가 수행하는 검증 로직 중 일부를 에이전트가 직접 수행하고 실패 시 스스로 교정하는 'Autonomous Pre-Commit' 노드가 필요함.
