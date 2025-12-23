# Next Session

## Session Goal
- **Proactive Self-Cleanup & Artifact Pruning**: 작업 과정에서 생성되는 수많은 임시 파일, 오래된 백업(`*.bak`), 버전 관리 잔해들을 시스템이 스스로 분석하여, 불필요한 데이터를 주기적으로 삭제하고 '최소한의 가벼운 상태'를 유지하는 자율 청소 지능을 구현한다.

## Context
- `write_file` 도구가 실행될 때마다 자동 백업과 버전 아카이빙이 수행되면서 `logs/` 디렉토리의 크기가 급격히 팽창하고 있음.
- 시스템의 속도와 효율을 위해, 7일 이상 지나거나 중복된 데이터는 압축 후 삭제하는 등의 '데이터 가지치기'가 필수적임.
- 이는 단순한 삭제가 아닌, 지능적인 '가치 평가' 기반의 관리여야 함.

## Scope
### Do
- `agents/analyst/base.py`: 파일의 생성일과 사용 빈도를 분석하여 삭제 대상을 선별하는 `evaluate_artifact_value` 메서드 추가.
- `utils/tools.py`: 대량의 임시 파일을 안전하게 소거하는 `safe_bulk_delete` 유틸리티 구현.
- `main.py`: 세션 종료 또는 에너지 회복 루프 시점에 주기적으로 자율 청소를 수행하도록 트리거 연동.

### Do NOT
- `experience.json`(샤드)이나 `trace.jsonl` 요약본 등 시스템 지능과 직결된 데이터는 절대 삭제하지 않음.

## Expected Outputs
- `agents/analyst/base.py` (Cleanup logic)
- `utils/tools.py` (Safe delete utility)
- `tests/test_self_cleanup.py` (New)

## Completion Criteria
- 7일 이상 된 백업 파일이 존재할 때, 청소 루틴 실행 후 해당 파일들이 성공적으로 제거되어야 함.
- 청소 후 시스템 전체 용량(logs 기준)이 유의미하게 감소해야 함.
- `docs/sessions/session_0116.md` 기록.