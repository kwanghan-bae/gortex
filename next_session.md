# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Spatial Reasoning SDK & WebXR Foundation Complete (v2.2.8)

## 🧠 Current Context
공간 추론을 위한 기초 SDK가 마련되었습니다. 이제 Gortex의 지식과 사고 과정은 VR/AR 기기에서 상호작용 가능한 3D 데이터로 변환되어 스트리밍되며, 이는 가상 공간에서의 지능형 협업을 위한 핵심 인프라가 됩니다.

## 🎯 Next Objective
**Energy-Aware Tasking (Work-Life Balance for AI)**
1. **`Energy Simulation`**: 에이전트에게 가상의 '에너지(Battery)' 상태를 부여합니다. 복잡한 추론이나 대규모 도구 호출은 에너지를 많이 소모하며, 에너지가 낮아지면 에이전트는 더 가벼운 모델을 사용하거나 '휴식(Sleep/Summarization)'을 스스로 결정합니다.
2. **`Efficiency Scoring`**: 에너지 소모 대비 성과를 측정하여, 최소한의 자원으로 최대의 결과를 내는 '고효율 추론 경로'를 스스로 학습하도록 보상 로직을 강화합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 공간 추론 SDK 및 WebXR 기초 완료 (v2.2.8).
- 다음 목표: 에너지 인지형 작업 관리(Energy-Aware Tasking).

작업 목표:
1. `core/state.py`에 에이전트의 현재 에너지 상태를 저장하는 `agent_energy` 필드를 추가해줘.
2. `agents/manager.py`에서 에너지 수준에 따라 모델을 변경하거나 작업 강도를 조절하는 지능형 스케줄링 로직을 구현해줘.
```