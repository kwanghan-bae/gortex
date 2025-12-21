# Next Session

## Session Goal
- 수정 파일 기반 증분 테스트 수행 (Selective Testing v1)

## Context
- `Autonomous Pre-Commit` 도입으로 매번 `pre_commit.sh`가 실행되면서, 프로젝트 규모가 커질수록 전체 테스트 실행 시간이 개발 생산성을 저해하는 요소가 됨.
- `file_cache`의 해시 불일치를 감지하여 '변경된 파일'을 식별하고, `Dependency Impact Analyzer`를 통해 관련 모듈만 선별하여 테스트하는 스마트 테스트 스케줄링이 필요함.

## Scope
### Do
- `utils/tools.py`에 변경된 파일 리스트를 추출하는 `get_changed_files` 메서드 추가.
- `scripts/pre_commit.sh`를 확장하여 선택적 테스트 실행 옵션(`--selective`) 지원.
- `agents/coder.py`에서 자율 검증 시 전체 테스트 대신 영향 범위 내의 테스트만 실행하도록 최적화.

### Do NOT
- 위험도가 높은 'Master' 브랜치 배포 전 검증 시에는 여전히 전체 테스트를 수행할 것.

## Expected Outputs
- `utils/tools.py`, `scripts/pre_commit.sh`, `agents/coder.py` 수정.

## Completion Criteria
- 특정 파일 수정 후 자율 검증 시, 수정된 파일과 관련된 테스트만 실행되어 전체 검증 시간이 50% 이상 단축되는 것이 확인되어야 함.