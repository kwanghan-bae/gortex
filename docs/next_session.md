# Next Session

## Session Goal
- 에이전트 주도형 자동 검증 및 자가 수정 (Autonomous Pre-Commit v1)

## Context
- 현재 `pre_commit.sh`는 `main.py` 외부에서 별도로 실행되거나, 에이전트가 그 결과를 비판적으로 수용해야 함.
- 에이전트가 코드를 작성한 즉시 스스로 `pre_commit.sh`를 실행하고, 실패 로그를 분석하여 즉각적인 '수정 루프'를 도는 자동화된 노드 또는 로직이 필요함.

## Scope
### Do
- `agents/coder.py` (또는 신규 노드)에서 작업 완료 직전 `scripts/pre_commit.sh`를 직접 실행하는 단계 추가.
- 실행 실패 시 오류 로그를 `Analyst`에게 전달하여 RCA 및 교정 지침을 획득.
- 통과할 때까지 최대 3회 자가 수정을 시도하는 지능형 루프 구축.

### Do NOT
- 실제 커밋(`git commit`)은 수행하지 말 것 (오직 검증과 수정만 자동화).

## Expected Outputs
- `agents/coder.py` 또는 신규 노드 수정, `utils/tools.py` 보강.

## Completion Criteria
- 오류가 있는 코드를 작성했을 때, 에이전트가 스스로 `pre_commit` 실패를 인지하고 수정한 뒤 통과시키는 전 과정이 확인되어야 함.
