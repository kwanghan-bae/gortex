# Session 0032

## Goal
- 테스트 코드 작성 강화 및 pre-commit 자동 검증 고도화

## What Was Done
- **scripts/pre_commit.sh 업그레이드 (v1.3)**: 
    - Ruff를 이용한 린팅(Linting) 추가.
    - **Strict Mode**: 신규 로직 파일 추가 시 테스트 파일(`tests/test_*.py`)이 없으면 커밋을 강제 차단하는 로직 구현.
    - Coverage 측정 및 리포트 출력 기능 추가.
    - 패키지 임포트 오류 해결을 위한 `PYTHONPATH` 및 `unittest discover` 실행 로직 고도화.
- **docs/RULES.md 강화**: 'Test-First' 원칙과 엄격한 테스트 존재 여부 검사를 프로젝트 계약으로 명문화.
- **docs/prompts/core_agents.yaml 보강**: Planner와 Coder가 테스트 시나리오 설계를 최우선 단계로 인식하도록 지침 개편.

## Decisions
- 테스트 없는 코드는 기술 부채로 간주하며, `pre_commit.sh`를 통과하지 못하는 작업은 '실패'로 정의함.
- 에이전트가 `pre_commit.sh`의 모든 메시지(경고 포함)를 정독하고 판단하도록 강제함.

## Problems / Blockers
- 현재 환경에 `ruff`나 `coverage` 라이브러리가 설치되어 있지 않을 경우 기본 검증으로 폴백함. 향후 `setup.sh`를 통해 필수 설치를 권장해야 함.

## Notes for Next Session
- 강화된 테스트 규정을 바탕으로, 실제 시스템의 안정성을 높이기 위한 '핵심 에이전트(Manager, Planner) 로직의 엣지 케이스 테스트' 보강이 필요함.
