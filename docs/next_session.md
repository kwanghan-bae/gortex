# Next Session

## Session Goal
- 기술 부채 자동 해소를 위한 Auto-Refactor Loop 가동

## Context
- v2.2.19에서 도입된 'Code Complexity Heatmap'을 통해 프로젝트의 취약 지점이 가시화됨.
- 이제 `Analyst`가 식별한 고복잡도 파일을 대상으로, `Manager`와 `Planner`가 리팩토링 계획을 세우고 `Coder`가 실행하는 자동 개선 순환 구조를 완성해야 함.

## Scope
### Do
- `agents/analyst.py`에서 가장 복잡한 파일을 우선적으로 리팩토링 후보로 추천하는 `suggest_refactor_target` 로직 추가.
- `agents/manager.py`에서 시스템 부하가 적을 때(Energy > 80) 자동 리팩토링 작업을 승인하고 `planner`로 라우팅하는 지능형 스케줄링 구현.
- 리팩토링 후 반드시 기존 단위 테스트와 신규 테스트를 모두 통과해야 함을 명시.

### Do NOT
- 한 번에 여러 파일을 수정하지 말 것 (파일 단위로 순차적 진행).
- 프로젝트의 핵심 설정 파일 수정 금지.

## Expected Outputs
- `agents/analyst.py`, `agents/manager.py` 수정.

## Completion Criteria
- `/scan_debt` 결과 상위 파일 중 하나를 대상으로 리팩토링 계획이 수립되고, 수정 후 테스트가 통과하는 과정이 확인되어야 함.