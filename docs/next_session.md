# Next Session

## Session Goal
- **Intelligent Resource Scaling & Token Budgeting**: 일일 API 사용 예산(토큰 및 비용)을 관리하고, 예산 소진 속도에 따라 시스템이 스스로 사용하는 모델의 지능 수준(Pro -> Flash -> Lite -> Ollama)을 하향 조정하는 '자율 경제 방어' 시스템을 구축한다.

## Context
- 현재 모델 선택은 에이전트 등급에만 의존함.
- API 할당량이 부족하거나 하루 목표 비용을 초과할 위험이 있을 때, 고평판 에이전트라도 강제로 경량 모델을 쓰게 하여 전체 가용성을 유지해야 함.
- 이는 장기적인 운영 안정성을 보장하기 위함임.

## Scope
### Do
- `core/config.py`: `DAILY_COST_BUDGET` 설정 추가.
- `utils/efficiency_monitor.py`: 당일 누적 비용(`daily_cumulative_cost`) 계산 기능 추가.
- `core/llm/factory.py`: `get_model_for_grade` 메서드에 '예산 가중치(Budget Scale)'를 반영하여 모델을 하향(Downgrade)하는 로직 구현.

### Do NOT
- 실제 카드 결제나 외부 청구 데이터와 연동하지 않음 (시스템 내 추정치 기준).

## Expected Outputs
- `utils/efficiency_monitor.py` (Update)
- `core/llm/factory.py` (Update)
- `tests/test_budget_scaling.py` (New)

## Completion Criteria
- 하루 예산이 $0.10 인데 이미 $0.09를 썼을 경우, 다이아몬드 등급 에이전트에게도 Pro가 아닌 Flash 또는 Lite 모델이 할당되어야 함.
- `docs/sessions/session_0099.md` 기록.
