# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Virtual Cursor & Precision Editing Complete (v2.0.0)

## 🧠 Current Context
정밀 편집 도구(Virtual Cursor)가 도입되어 이제 Gortex는 대규모 소스 코드의 특정 부분만 핀포인트로 수정할 수 있습니다. 이는 시스템의 정확도를 높이고, 특히 복잡한 리팩토링이나 버그 수정 시의 안정성을 획기적으로 향상시킵니다.

## 🎯 Next Objective
**Predictive Pre-fetching (Latency Optimization)**
1. **`Predictive Pre-fetching`**: 에이전트가 현재 단계를 수행하는 동안, 다음 단계에서 필요할 것으로 예상되는 도구 결과(파일 읽기, 웹 검색 등)를 미리 백그라운드에서 준비합니다.
2. **`Parallel Speculation`**: 여러 가능한 시나리오를 미리 병렬로 추론(Speculative Execution)하여, 에이전트의 실제 결정 시점에서의 대기 시간을 최소화합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 가상 커서 및 정밀 편집 시스템 완료 (v2.0.0).
- 다음 목표: 실행 지연 시간 최적화를 위한 사전 예측 로딩(Predictive Pre-fetching).

작업 목표:
1. `agents/planner.py`에서 다음 단계(Next Step)를 예측하여 미리 필요한 파일을 로드하도록 지침을 보강해줘.
2. `main.py`의 스트리밍 루프를 개선하여 에이전트가 생각하는 동안 다음 예상 도구의 결과를 미리 준비하는 기초 인프라를 구상해줘.
```