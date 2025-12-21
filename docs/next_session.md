# Next Session

## Session Goal
- 인터랙티브 의사결정 학습 및 사용자 선호도 모델링 (Decision Learning v1)

## Context
- 현재 에이전트들은 주로 과거 로그나 규칙에 의존하여 판단하고 있음.
- 하지만 미묘한 설계 선택(A 기술 vs B 기술)이나 사용자의 주관적 취향이 개입되는 지점에서는 명시적인 질문이 필요함.
- 에이전트가 "이런 이유로 A를 선택하려는데 괜찮으신가요?"라고 묻고, 사용자의 피드백을 `EvolutionaryMemory`에 즉시 기록하는 기능이 필요함.

## Scope
### Do
- `agents/manager.py`에 불확실성이 높거나 트레이드오프가 뚜렷한 경우 '사용자 개입 요청(Request User Input)'을 생성하는 로직 추가.
- 사용자의 응답을 분석하여 새로운 '사용자 선호도 규칙'을 생성하는 `AnalystAgent.learn_from_interaction` 메서드 추가.
- 대시보드 UI에 질문 패널 하이라이트 기능 보강.

### Do NOT
- 모든 사소한 단계에서 질문하지 말 것 (에너지/효율성 기반으로 꼭 필요한 경우만 질문).

## Expected Outputs
- `agents/manager.py`, `agents/analyst.py`, `ui/dashboard.py` 수정.

## Completion Criteria
- 에이전트가 작업을 멈추고 사용자에게 질문을 던지는 상황이 발생하고, 답변 후 해당 내용이 새로운 규칙으로 저장되는 과정이 확인되어야 함.