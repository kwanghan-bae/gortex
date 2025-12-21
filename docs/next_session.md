# Next Session

## Session Goal
- 사고 과정의 능동적 지식화 및 회상 시스템 (Thought Memorization v1)

## Context
- 현재는 외부 트렌드나 사용자 매크로 위주로 지식이 쌓이고 있음.
- 하지만 에이전트가 복잡한 디버깅이나 설계를 마친 후의 '깨달음'은 세션이 끝나면 휘발되는 경향이 있음.
- `Analyst`가 매 턴 종료 시 에이전트의 사고 트리(`thought_tree`)를 분석하여, 미래에 가치 있는 '추론 패턴'을 추출하고 이를 벡터 지식으로 저장해야 함.

## Scope
### Do
- `agents/analyst.py`에 사고 과정을 요약하여 지식으로 변환하는 `memorize_valuable_thought` 메서드 추가.
- `main.py` 스트리밍 루프 마지막에 의미 있는 사고를 선별하여 저장하도록 연동.
- 저장 시 `type="reasoning_pattern"` 메타데이터를 활용하여 나중에 `Recall` 시 우선순위 부여.

### Do NOT
- 모든 사소한 생각을 다 저장하지 말 것 (확신도나 결과 성과가 높은 것 위주로 선별).

## Expected Outputs
- `agents/analyst.py`, `main.py` 수정.

## Completion Criteria
- 복잡한 문제 해결 후, 지식 베이스에 "이런 상황에서는 저런 식으로 접근하는 것이 효율적임"과 같은 추론 패턴이 저장되는 것이 확인되어야 함.
