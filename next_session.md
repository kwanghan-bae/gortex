# ⏭️ Gortex Next Session Context

**Date:** 2024-12-21
**Status:** Efficiency Scoring & Self-Optimization Complete (v2.2.10)

## 🧠 Current Context
효율성 점수 계산(`calculate_efficiency_score`)과 우수 패턴 승격(`promote_efficient_pattern`) 로직이 구현되었습니다. 이제 이 도구들을 실제 에이전트의 의사결정 과정(Swarm, Manager)에 통합하여 실질적인 성능 향상을 이끌어내야 합니다.

## 🎯 Next Objective
**Advanced Efficiency Integration (Swarm & Manager)**
1. **`Swarm Efficiency`**: `agents/swarm.py`에서 병렬 작업 결과 취합 시, 단순 확신도(Certainty)뿐만 아니라 효율성 점수를 반영하여 최적의 안(Winner)을 선정하도록 로직을 개선합니다.
2. **`Manager Insight`**: `agents/manager.py`의 사고 과정에 현재 세션의 평균 효율성 점수를 참고하여 모델 선택이나 전략 수정에 반영하도록 합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 효율성 점수 및 패턴 승격 로직 구현 완료 (v2.2.10).
- 다음 목표: Swarm 및 Manager에 효율성 지표 통합.

작업 목표:
1. `agents/swarm.py`에서 `AnalystAgent.calculate_efficiency_score`를 호출하여 병렬 작업의 순위를 매기는 로직을 추가해줘.
2. `agents/manager.py`에서 최근 작업의 효율성이 낮을 경우(예: < 40), 더 신중한 계획(Detailed Planning)을 수립하도록 프롬프트를 동적 조정해줘.
```