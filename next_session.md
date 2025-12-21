# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Predictive Pre-fetching & Latency Optimization Complete (v2.0.1)

## 🧠 Current Context
예측 로딩(Predictive Pre-fetching) 인프라가 구축되어 에이전트의 작업 흐름이 훨씬 매끄러워졌습니다. Planner가 미래를 내다보고 리소스를 미리 준비하며, 이는 전체적인 시스템 응답 속도 향상에 기여합니다.

## 🎯 Next Objective
**Speculative Reasoning (Parallel Scenarios)**
1. **`Scenario Branching`**: 에이전트가 불확실한 상황에서 하나의 답변을 기다리는 대신, 여러 가능한 가설(예: 해결책 A, B, C)을 동시에 병렬로 추론합니다.
2. **`Winner Selection`**: 생성된 여러 시나리오 중 가장 자가 일관성(Self-Consistency)이 높고 위험이 낮은 최적의 결과를 선택하여 사용자에게 최종 답변으로 제공합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 예측 로딩 시스템 완료 (v2.0.1).
- 다음 목표: 병렬 가설 추론 엔진(Speculative Reasoning) 구축.

작업 목표:
1. `agents/manager.py` 또는 `swarm` 노드를 확장하여, 하나의 쿼리에 대해 서로 다른 프롬프트 전략을 가진 여러 에이전트를 동시에 가동하는 로직을 작성해줘.
2. 각 시나리오의 결과 점수를 매기고 최적의 답변을 선별하는 `Scenario Evaluator` 기능을 구현해줘.
```
