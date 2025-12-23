# Next Session

## Session Goal
- **Intelligent Feedback Loop Optimization**: 시스템 내부의 성공/실패 데이터를 더욱 정밀하게 분석하여, 에이전트의 평판 점수(`agent_economy`)와 경험 규칙(`Experience Rules`)의 강화 및 약화에 즉각적이고 정확하게 반영하는 '초정밀 피드백 엔진'을 구축한다.

## Context
- 현재 피드백은 성공 시 +10, 실패 시 -5와 같이 다소 단순하게 작동함.
- 작업의 난이도, 소모된 리소스 대비 성과, 그리고 사용자 만족도를 종합한 '가중 피드백' 체계가 필요함.
- 이는 에이전트들이 더 효율적이고 똑똑한 경로를 스스로 선택하도록 만드는 진화의 가속기임.

## Scope
### Do
- `utils/economy.py`: 작업 난이도(Complexity)와 성과(Quality)를 결합한 `calculate_weighted_reward` 로직 추가.
- `agents/analyst/reflection.py`: 사후 분석 시 실패 원인이 '지능 부족'인지 '리소스 부족'인지 판별하여 피드백 방향성 결정.
- `core/evolutionary_memory.py`: 성과가 누적된 규칙에 대해 '검증된 지혜(Certified Wisdom)' 배지 부여 및 프롬프트 우선순위 격상.

### Do NOT
- 외부 보상 시스템 연동은 고려하지 않음 (순수 내부 알고리즘 고도화).

## Expected Outputs
- `utils/economy.py` (Weighted Reward)
- `agents/analyst/reflection.py` (Precision Feedback)
- `tests/test_precision_feedback.py` (New)

## Completion Criteria
- 고난도 작업을 적은 토큰으로 성공했을 때, 일반 작업보다 최소 3배 이상의 포인트가 지급되어야 함.
- 반복적인 성공을 이끈 규칙이 프롬프트 상단에 우선적으로 배치되는지 확인.
- `docs/sessions/session_0117.md` 기록.
