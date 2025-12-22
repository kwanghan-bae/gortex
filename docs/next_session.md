# Next Session

## Session Goal
- **Autonomous Backup & Knowledge Archiving**: 시스템이 누적된 대화 로그와 지능 데이터를 주기적으로 정리(Garbage Collection)하고, 핵심 지식 파일인 `experience.json`을 안전하게 백업하여 데이터 손실을 방지한다.

## Context
- 대화 세션이 90개를 넘어서면서 로그 폴더와 지식 파일의 크기가 점차 커지고 있음.
- 파일 손상이나 예기치 못한 유실에 대비하여, 시스템 스스로가 '백업 사본'을 만들고 관리할 필요가 있음.
- `Analyst` 에이전트의 역할 중 '기록 관리' 능력을 실체화함.

## Scope
### Do
- `utils/tools.py`: `backup_file_with_rotation` 함수 추가 (최근 5개 버전 유지).
- `agents/analyst/base.py`: 주기적으로 로그를 압축하여 아카이브 폴더로 이동시키는 `archive_system_logs` 구현.
- `core/graph.py`: 세션 종료 전 또는 특정 주기마다 `analyst`가 아카이빙을 수행하도록 트리거 연동.

### Do NOT
- 실제 클라우드 스토리지(S3 등) 연동은 배제 (로컬 파일 시스템 내 백업 집중).

## Expected Outputs
- `utils/tools.py` (Update)
- `agents/analyst/base.py` (Update)
- `logs/backups/` (New Directory for backups)

## Completion Criteria
- `experience.json` 파일의 백업 사본이 `logs/backups/`에 날짜별로 생성되어야 함.
- 30일 이상 지난 로그 파일이 ZIP으로 압축되어 `logs/archives/`로 이동해야 함.
- `docs/sessions/session_0096.md` 기록.