# Next Session

## Session Goal
- 아키텍처 및 정책 준수 실시간 검증 (Constraint Validator v1)

## Context
- `EvolutionaryMemory`를 통해 시스템 규칙이 늘어나고 있으나, 실행 시점에 이 규칙들이 정말 지켜졌는지 체크하는 프로세스가 `Analyst`의 사후 검증에만 의존하고 있음.
- `Coder`가 도구를 호출하기 직전, 현재 활성화된 제약 조건(`active_constraints`)을 위반하는지 실시간으로 스캔하고 경고하는 전용 노드 또는 가드 로직이 필요함.

## Scope
### Do
- `agents/analyst.py`에 제약 조건 위반 여부를 정밀 판정하는 `validate_constraints` 메서드 추가.
- `agents/coder.py`에서 도구 호출 전 이 검증 로직을 거치도록 워크플로우 통합.
- 위반 시 즉시 중단하고 사용자에게 '정책 위반' 사유를 보고함.

### Do NOT
- 단순 스타일(PEP8) 검사와 혼동하지 말 것 (비즈니스/아키텍처 규칙 중심).

## Expected Outputs
- `agents/analyst.py`, `agents/coder.py` 수정.

## Completion Criteria
- 활성화된 규칙(예: "특정 모듈은 수정 금지")을 위반하는 코드를 작성하려 할 때, 시스템이 이를 즉시 감지하고 실행을 차단하는 것이 확인되어야 함.