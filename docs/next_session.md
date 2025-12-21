# Next Session

## Session Goal
- 자율적 로그 압축 및 데이터 백업 시스템 (Autonomous Backup v1)

## Context
- `logs/` 디렉토리에 지식 샤드, 세션 파일, 인덱스 등 중요한 데이터가 산재해 있음.
- `Analyst`가 세션 종료 시 주요 데이터들을 하나의 아카이브(`.zip` 또는 `.tar.gz`)로 압축하고, `logs/backups/full_session_XXXX.zip` 형태로 보관하는 로직이 필요함.

## Scope
### Do
- `utils/tools.py`에 디렉토리 압축 및 해제 유틸리티 추가.
- `agents/analyst.py`에 전체 세션 데이터를 패키징하는 `perform_full_backup` 메서드 추가.
- `main.py` 종료 시점에 증분 정리가 아닌 '전체 백업' 옵션을 트리거 가능하게 연동.

### Do NOT
- `venv`나 `.git` 같이 불필요하게 거대한 폴더는 백업 대상에서 제외할 것.

## Expected Outputs
- `utils/tools.py`, `agents/analyst.py`, `main.py` 수정.

## Completion Criteria
- 세션 종료 후, `logs/backups/` 내에 현재 세션의 모든 정수가 담긴 압축 파일이 생성되는 것이 확인되어야 함.
