# Next Session

## Session Goal
- **Multi-Model Strategy Selection**: 에이전트의 평판 등급(`agent_economy`)과 작업의 중요도(`priority`)에 따라 사용할 LLM 모델(Gemini-Pro, Flash, Ollama 등)을 스스로 선택하는 지능형 리소스 할당 시스템을 구축한다.

## Context
- `Session 0089`에서 평판 대시보드를 안착시킴.
- 현재 모든 에이전트가 등급에 상관없이 비슷한 모델을 사용하고 있음.
- '다이아몬드' 등급 에이전트에게는 Pro 모델을, '브론즈'에게는 경량 모델을 할당하여 비용을 절감하고 실적에 따른 인센티브를 제공함.

## Scope
### Do
- `core/llm/factory.py`: 등급별 모델 권한 맵(`GRADE_MODEL_MAP`) 정의.
- `agents/manager.py`: 작업 할당 시 에이전트의 등급을 체크하여 `assigned_model`을 동적으로 결정하는 로직 구현.
- `utils/economy.py`: 특정 작업 완수 시 등급 승급을 축하하는 '업적(Achievement)' 알림 기능 보강.

### Do NOT
- 실제 API 비용 결제 시스템 연동은 하지 않음.

## Expected Outputs
- `core/llm/factory.py` (Update)
- `agents/manager.py` (Update)
- `tests/test_model_selection.py` (New)

## Completion Criteria
- 평판 점수가 낮은(브론즈) 에이전트에게는 자동으로 `flash-lite` 또는 `Ollama` 모델이 할당되어야 함.
- `docs/sessions/session_0090.md` 기록.