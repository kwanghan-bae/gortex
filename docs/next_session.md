# Next Session

## Session Goal
- 자율적 작업 공간 구조화 및 아카이빙 (Workspace Organizer v1)

## Context
- 현재 `logs/backups`, `logs/versions`, `tests/` 등에 수많은 파일이 누적되고 있으나, 이를 프로젝트 맥락에 맞게 정리하는 로직이 없음.
- `Analyst`가 세션 종료 시점에 생성된 파일들의 중요도를 판정하고, 불필요한 임시 파일은 삭제하며 중요한 버전은 `archive/project_name/vX.X.X/`로 이동시키는 자율 정리 지능이 필요함.

## Scope
### Do
- `agents/analyst.py`에 작업 공간을 분석하고 정리 계획을 세우는 `organize_workspace` 메서드 추가.
- `utils/tools.py`에 파일 이동 및 구조화된 아카이빙을 위한 유틸리티 추가.
- `main.py` 종료 시점에 자율 정리를 트리거.

### Do NOT
- 사용자의 소스 코드를 동의 없이 삭제하지 말 것 (오직 생성된 부속물 위주로 정리).

## Expected Outputs
- `agents/analyst.py`, `utils/tools.py`, `main.py` 수정.

## Completion Criteria
- 세션 종료 후, `logs/archives/` 폴더 내에 현재 작업 내용이 깔끔하게 구조화되어 보관되는 것이 확인되어야 함.