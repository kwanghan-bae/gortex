# Next Session

## Session Goal
- **Intelligent Knowledge Pruning & Semantic Garbage Collection**: 지식 베이스에 축적된 수많은 경험 규칙(Experience Rules) 중, 오랫동안 사용되지 않았거나 성공률이 현저히 낮은 노후 지식을 스스로 식별하여 제거(GC)하고, 유사한 고성과 규칙들을 시맨틱 군집화(Semantic Clustering)를 통해 하나의 강력한 지침으로 병합함으로써 지능의 밀도를 극한으로 끌어올린다.

## Context
- 시스템이 오래 운영됨에 따라 수백 개의 자잘한 규칙들이 쌓여 프롬프트의 토큰을 낭비하고 인지적 노이즈를 유발하고 있음.
- 단순히 병합하는 것이 아니라, 규칙의 '생존 가치'를 평가하여 가치가 낮은 것은 과감히 소거하는 '지식 다윈주의'가 필요함.
- 이는 에이전트가 항상 가장 순도 높은 지혜만을 참조하게 만드는 성능 최적화의 정점임.

## Scope
### Do
- `core/evolutionary_memory.py`: 규칙의 성공률과 마지막 사용 시점을 기반으로 '가치 점수'를 산출하는 `calculate_rule_value` 로직 추가.
- `agents/analyst/base.py`: 가치가 낮은 규칙들을 소거하고 유사 규칙들을 통합하는 `garbage_collect_knowledge` 기능 구현.
- `main.py`: 세션 종료 또는 일정 주기마다 '지능 최적화' 트리거를 발생시켜 자율 청소 수행.

### Do NOT
- 'Certified Wisdom'이나 최근 3회 세션 내 생성된 신규 지식은 가치 점수와 상관없이 보존함.

## Expected Outputs
- `core/evolutionary_memory.py` (Value Calculation)
- `agents/analyst/base.py` (Knowledge GC)
- `tests/test_memory_optimization.py` (New)

## Completion Criteria
- 성공률 20% 미만이거나 10세션 이상 미사용된 일반 규칙 3개 이상이 정확히 소거되어야 함.
- 유사한 의미를 가진 규칙 2개가 하나로 병합되어야 함.
- `docs/sessions/session_0127.md` 기록.
