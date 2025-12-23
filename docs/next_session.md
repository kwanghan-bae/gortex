# Next Session

## Session Goal
- **Intelligent Model Selection & Context Budgeting**: 에이전트의 평판(`points`), 작업의 위험도(`risk_score`), 그리고 오늘의 남은 토큰 예산을 종합 분석하여 Gemini Pro, Flash, Ollama 중 최적의 모델을 자동으로 선택하고, 예산 초과 시 컨텍스트를 지능적으로 압축하는 '하이브리드 리소스 최적화'를 달성한다.

## Context
- 현재 모델 선택은 Manager가 단순히 에이전트 이름에 따라 할당하거나 하드코딩된 정책을 따름.
- 토큰 할당량이 부족하거나 로컬 환경이 쾌적할 때는 Ollama로 부하를 분산해야 함.
- 또한, 컨텍스트가 길어질 때 무조건 요약하는 것이 아니라, 중요도가 낮은 메시지만 골라내는 '가지치기(Pruning)' 기술이 필요함.

## Scope
### Do
- `core/engine.py`: 모델 선택 지능이 강화된 `DynamicModelOrchestrator` 로직 통합.
- `utils/token_counter.py`: 오늘 하루 사용된 토큰량을 추적하는 `DailyTokenTracker` 구현.
- `core/state.py`: `risk_score` 필드 추가 및 모델 할당 판단 근거 기록.

### Do NOT
- 실제 모델의 가중치나 매개변수 수정은 하지 않음 (외부 호출 로직 최적화).

## Expected Outputs
- `core/engine.py` (Dynamic Selection)
- `utils/token_counter.py` (Token Tracker)
- `tests/test_model_selection.py` (New)

## Completion Criteria
- 에이전트 평판이 1000점 미만일 때, 고난도 작업이 아니면 자동으로 `gemini-2.0-flash` 또는 `ollama`가 할당되어야 함.
- 일일 토큰 한도의 80%에 도달하면 강제로 컨텍스트 압축 모드가 활성화되어야 함.
- `docs/sessions/session_0118.md` 기록.