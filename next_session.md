# ⏭️ Gortex Next Session Context

**Date:** 2024-12-21
**Status:** Energy-Aware Tasking Foundation Complete (v2.2.9)

## 🧠 Current Context
에이전트에게 '에너지(Energy)' 개념이 도입되었습니다. `agent_energy` 상태에 따라 Manager는 자동으로 더 가벼운 모델을 선택하거나 작업 강도를 조절합니다. 이제 이 시스템을 바탕으로 에너지 효율성을 극대화하는 학습 루프가 필요합니다.

## 🎯 Next Objective
**Efficiency Scoring & Self-Optimization**
1. **`Efficiency Metric`**: (성공한 작업의 가치) / (소모된 토큰 + 시간 + 에너지) 공식을 정의하여 에이전트의 효율성을 정량화합니다.
2. **`Reward Logic`**: 높은 효율성을 보인 작업 패턴(Thought Tree)을 `EvolutionaryMemory`에 우선적으로 저장하여, 시스템이 스스로 "최소 노력, 최대 성과"를 지향하도록 진화시킵니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 에너지 인지형 작업 관리 기초 구현 완료 (v2.2.9).
- 다음 목표: 효율성 점수(Efficiency Scoring) 및 자가 최적화 보상 로직.

작업 목표:
1. `agents/analyst.py`에 작업 완료 후 효율성 점수를 계산하는 `calculate_efficiency_score` 메서드를 구현해줘.
2. `core/evolutionary_memory.py`와 연동하여 높은 효율성을 보인 패턴을 강화 학습(규칙 승격)하는 로직을 추가해줘.
```
