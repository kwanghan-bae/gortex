# Next Session

## Session Goal
- **Heuristic Memory Pruning & Ranking**: 누적된 자가 진화 규칙(`Experience Rules`)의 기여도를 평가하여, 실제 작업 성공률에 영향을 주지 못하는 저가치 규칙을 폐기하거나 유사한 규칙끼리 병합하여 지식 베이스를 슬림하게 유지한다.

## Context
- 현재 규칙이 무분별하게 쌓이면서 프롬프트 크기가 증가하고 모델의 인지적 노이즈가 발생하고 있음.
- 배운 것을 기억하는 것만큼, 잊어야 할 것을 잊는 '지능적 망각'이 필요함.
- `experience.json`의 각 규칙에 성공 기여 횟수(`usage_count`)와 성공률(`impact_rate`)을 도입함.

## Scope
### Do
- `core/evolutionary_memory.py`: 규칙별 사용 통계(Usage Tracking) 필드 및 로직 추가.
- `agents/analyst/base.py`: 규칙의 유효성을 평가하고 최적화(Pruning/Merging)를 수행하는 `optimize_knowledge_base` 구현.
- `utils/tools.py`: 지식 베이스 최적화 전후의 토큰 절감 효과 측정 유틸리티 추가.

### Do NOT
- 사용자가 수동으로 작성한 규칙은 절대 삭제하지 않음 (시스템 자동 생성 규칙만 대상).

## Expected Outputs
- `core/evolutionary_memory.py` (Update)
- `agents/analyst/base.py` (Update)
- `tests/test_memory_optimization.py` (New)

## Completion Criteria
- 10개의 중복되거나 무의미한 규칙이 있을 때, 최적화 후 핵심 규칙 2~3개로 압축되어야 함.
- `docs/sessions/session_0092.md` 기록.