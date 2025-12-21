# Next Session

## Session Goal
- 핵심 에이전트(Manager, Planner) 로직의 엣지 케이스 테스트 보강

## Context
- v2.6.1을 통해 엄격한 테스트 체계가 마련됨.
- 하지만 현재 기존 테스트들은 기본 경로(Happy Path) 위주로 구성되어 있어, 복잡한 사용자 요청이나 예외 상황에서의 복원력을 충분히 보장하지 못함.
- `manager_node`와 `planner_node`를 대상으로 비정상 입력, Quota 초과, 빈 컨텍스트 등 엣지 케이스에 대한 단위 테스트를 집중 보강해야 함.

## Scope
### Do
- `tests/test_manager.py` 및 `tests/test_planner.py` 확장.
- 에러 상황(API Failure, JSON Parsing Error 등)에서의 에이전트 반응성 테스트 추가.
- `Analyst`의 성찰적 디버깅(`generate_anti_failure_rule`)에 대한 단위 테스트 신설.

### Do NOT
- 실제 API 호출을 수행하지 말 것 (반드시 Mock 사용).

## Expected Outputs
- `tests/test_manager.py`, `tests/test_planner.py` 업데이트, `tests/test_analyst_reflection.py` 신설.

## Completion Criteria
- 모든 신규 엣지 케이스 테스트가 `pre_commit.sh` v1.3을 통과하고, 커버리지 리포트에서 해당 로직의 검증이 확인되어야 함.