# Next Session

## Session Goal
- 사용자의 다음 행동 예측 및 선제적 제안 (Predictive Next-Action v1)

## Context
- 현재 시스템은 사용자의 명시적인 명령이 있어야만 작동함.
- 에이전트가 작업 완료 후, 과거의 성공 패턴(ThoughtReflection)과 현재 맥락을 대조하여 사용자가 다음에 할 법한 행동(예: "방금 고친 코드 테스트해볼까요?")을 3개 이내로 예측하여 제안해야 함.

## Scope
### Do
- `agents/analyst.py`에 다음 작업(Next-Action)을 예측하는 `predict_next_actions` 메서드 추가.
- `main.py` 종료 시점에 예측된 액션들을 UI 상태로 전달.
- 대시보드 하단에 'Suggested Actions' 위젯 추가.

### Do NOT
- 사용자의 승인 없이 작업을 자동으로 실행하지 말 것 (오직 제안만 수행).

## Expected Outputs
- `agents/analyst.py`, `ui/dashboard.py`, `main.py` 수정.

## Completion Criteria
- 에이전트 작업 완료 시, 대시보드에 "다음에 이 작업을 하시겠습니까? 1. 테스트 실행 2. 문서화..."와 같은 제안이 표시되는 것이 확인되어야 함.
