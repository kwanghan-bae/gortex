# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Speculative Score & Probability Weighting Complete (v2.0.9)

## 🧠 Current Context
경험 기반의 시나리오 평가 엔진이 구축되었습니다. 이제 Gortex는 과거의 성공과 실패를 바탕으로 여러 가설 중 어떤 것이 가장 유망한지 정량적으로 판단할 수 있으며, 이는 특히 복잡하고 위험한 작업을 수행할 때 시스템의 안정성을 극대화합니다.

## 🎯 Next Objective
**Self-Healing Memory (Error-Solution Mapping)**
1. **`Healing Memory`**: 특정 도구가 실패했을 때 어떤 수정을 통해 해결했는지(Error-to-Solution)를 정교한 매핑 테이블로 기록합니다.
2. **`Instant Recovery`**: 유사한 에러가 다시 발생하면, 긴 추론 과정 없이 'Healing Memory'에서 즉시 해결책을 소환하여 1회 시도만에 수정을 완료하는 고속 복구 메커니즘을 구현합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 시나리오 평가 및 경험 가중치 시스템 완료 (v2.0.9).
- 다음 목표: 자가 수복 메모리(Self-Healing Memory) 구축.

작업 목표:
1. `core/evolutionary_memory.py` 또는 신규 `utils/healing_memory.py`를 통해 에러 패턴과 해결 코드 조각을 매핑하여 저장하는 기능을 추가해줘.
2. `coder` 노드에서 에러 발생 시 이 메모리를 최우선으로 검색하여 즉각적인 패치를 시도하는 로직을 보강해줘.
```
