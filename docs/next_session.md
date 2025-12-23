# Next Session

## Session Goal
- **Visual Knowledge Lineage**: 대시보드에 특정 지식(규칙)이 어떤 과거 사건(에러, 세션, 활동)으로부터 유래했는지 추적할 수 있는 '지식 계보(Lineage)' 시각화 기능을 구현하고, 이를 탐색할 수 있는 명령어를 추가한다.

## Context
- 시스템이 지식을 스스로 생성하고 병합함에 따라, "이 규칙은 대체 왜 생긴 거지?"라는 질문에 답할 수 있는 투명성이 필요함.
- `experience.json` (샤드)의 각 규칙은 이미 `context`, `source_session` 정보를 갖고 있지만, 이를 사용자가 보기 쉽게 표현하지 못하고 있음.
- 이는 AI의 블랙박스 문제를 해결하는 핵심 열쇠임.

## Scope
### Do
- `ui/dashboard.py`: 규칙 선택 시 해당 규칙의 히스토리와 근거 사례를 보여주는 `Knowledge Detail` 팝업 또는 패널 보강.
- `core/commands.py`: `/inspect [rule_id]` 명령어를 추가하여 지식의 뿌리를 텍스트 트리로 출력.
- `agents/analyst/base.py`: 지식 병합 시 원본 규칙들의 ID를 `parent_rules` 필드로 남겨 계보를 잇는 로직 추가.

### Do NOT
- 복잡한 3D 그래프는 구현하지 않음 (TUI 텍스트 트리 위주).

## Expected Outputs
- `ui/dashboard.py` (Detail view)
- `core/commands.py` (New /inspect command)
- `tests/test_knowledge_lineage.py` (New)

## Completion Criteria
- `/inspect` 명령 실행 시 해당 규칙의 원인 사건과 부모 규칙들이 트리 형태로 출력되어야 함.
- 대시보드의 `evolution` 패널에서 규칙 클릭 시 상세 정보가 노출되어야 함.
- `docs/sessions/session_0114.md` 기록.