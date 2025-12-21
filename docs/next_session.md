# Next Session

## Session Goal
- 성찰적 디버깅 및 실패 방지 규칙 자동 생성 (Reflective Debugging v1)

## Context
- `Coder`가 버그를 수정할 때 단순히 동작하게만 만드는 경향이 있어, 나중에 같은 실수가 반복될 수 있음.
- 테스트 실패 시 `Analyst`를 호출하여 오류의 근본 원인(RCA)을 분석하고, 이를 `EvolutionaryMemory`에 새로운 '제약 조건'으로 자동 등록해야 함.

## Scope
### Do
- `agents/coder.py`에서 테스트 실패 시 `Analyst`에게 RCA를 요청하는 로직 강화.
- `agents/analyst.py`에 오류 로그를 분석하여 '다시는 이런 실수를 하지 않기 위한 규칙'을 제안하는 `generate_anti_failure_rule` 메서드 추가.
- 생성된 규칙을 `experience.json`에 자동으로 반영하여 시스템의 면역력을 높임.

### Do NOT
- 단순 오타 수정까지 규칙으로 만들지 말 것 (논리적 모순이나 아키텍처 위반 중심).

## Expected Outputs
- `agents/coder.py`, `agents/analyst.py`, `core/evolutionary_memory.py` 수정.

## Completion Criteria
- 의도적으로 오류가 포함된 코드를 작성했을 때, 테스트 실패 -> 분석 -> 신규 규칙 생성 및 반영 과정이 확인되어야 함.