# Next Session

## Session Goal
- **Automated Bug Patching Loop**: 시스템 로그(`trace.jsonl`)에서 반복되는 에러 패턴을 감지하면, `Analyst`가 원인을 분석하고 `Coder`가 즉시 패치(Patch)를 생성하여 적용하는 '자율 수리 루프'를 고도화한다.

## Context
- 현재 에러가 발생하면 사람이 개입하거나 단순한 재시도를 수행함.
- 진화하는 시스템은 자신의 결함을 데이터로 인지하고, 코드 수준에서 영구적으로 수정할 수 있어야 함.
- `Session 0084`의 문서 치유와 결합하여 코드와 문서를 동시에 고치는 완결된 루프를 지향함.

## Scope
### Do
- `agents/analyst/reflection.py`: 에러 로그에서 코드 결함 지점을 특정하는 `diagnose_bug` 메서드 강화.
- `core/graph.py`: 특정 에러 발생 시 `manager`를 거치지 않고 즉시 `analyst` -> `coder`로 연결되는 'Emergency Patch Route' 추가.
- `utils/tools.py`: 패치 적용 전후의 시스템 상태를 비교하는 `verify_patch_integrity` 추가.

### Do NOT
- 하드웨어 장애나 네트워크 단절 등 외부 인프라 에러는 대상으로 하지 않음.

## Expected Outputs
- `agents/analyst/reflection.py` (Update)
- `core/graph.py` (Update)
- `tests/test_auto_patching.py` (New)

## Completion Criteria
- 인위적으로 `ZeroDivisionError`를 유발했을 때, 에이전트가 이를 감지하고 해당 코드를 수정한 뒤 테스트를 통과시켜야 함.
- `docs/sessions/session_0091.md` 기록.
