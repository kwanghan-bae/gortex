# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Immersive Reasoning & Timeline Scrubbing Complete (v2.0.8)

## 🧠 Current Context
몰입형 추론 UI와 타임라인 탐색 기능이 안착되었습니다. 이제 사용자는 Gortex의 사고 과정을 시간순으로 되돌려 보며 특정 결정이 왜 내려졌는지 정밀하게 복기할 수 있습니다. 이는 시스템의 설명 가능성(Explainability)을 한 차원 높여줍니다.

## 🎯 Next Objective
**Speculative Score & Probability Weighting**
1. **`Speculative Scoring`**: 병렬로 가동되는 여러 시나리오(`swarm`)에 대해, 과거의 성공 패턴과 현재의 제약 조건을 바탕으로 각 안의 성공 확률을 정교하게 예측합니다.
2. **`Adaptive Weighting`**: 단순히 최고 점수 하나만 선택하는 것이 아니라, 여러 유망한 안들에 가중치를 두어 혼합된 해결책을 도출하거나 순차적으로 시도하는 지능형 스케줄링을 구현합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 타임라인 기반 몰입형 UI 완료 (v2.0.8).
- 다음 목표: 시나리오별 성공 확률 예측 및 가중치 부여 로직 고도화.

작업 목표:
1. `agents/swarm.py`의 `scored_results` 계산 로직을 확장하여, 과거 로그의 유사 성공 사례 점수를 가중치로 반영하는 기능을 추가해줘.
2. 여러 시나리오가 비등한 점수를 가질 경우, 이를 사용자에게 보고하고 병합된 실행 계획을 제안하는 워크플로우를 보강해줘.
```