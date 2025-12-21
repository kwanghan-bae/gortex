# ⏭️ Gortex Next Session Context

**Date:** 2024-12-21
**Status:** Advanced Efficiency Integration Complete (v2.2.11)

## 🧠 Current Context
Swarm과 Manager가 이제 효율성 점수(`efficiency_score`)와 에너지 상태를 의사결정에 반영합니다. 시스템은 비효율적인 상황에서 더 신중하게 행동하며, 효율적인 패턴은 스스로 강화합니다. 이제 이 핵심 지표를 사용자가 직관적으로 볼 수 있도록 시각화해야 합니다.

## 🎯 Next Objective
**Real-time Efficiency Visualization**
1. **`Dashboard UI`**: Rich 터미널 대시보드에 현재 세션의 '평균 효율성'과 '에너지 잔량'을 보여주는 게이지(Gauge) 위젯을 추가합니다.
2. **`Web Broadcast`**: 웹 대시보드에도 실시간 효율성 데이터를 전송하여 그래프로 렌더링할 수 있도록 데이터 파이프라인을 확장합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 효율성 기반 의사결정 로직 통합 완료 (v2.2.11).
- 다음 목표: 터미널 및 웹 대시보드에 효율성/에너지 시각화.

작업 목표:
1. `ui/dashboard.py`의 사이드바에 에너지와 효율성을 표시하는 새로운 패널 또는 기존 패널 확장을 구현해줘.
2. `main.py`에서 매 턴마다 갱신된 에너지/효율성 정보를 UI로 전달하는 로직을 확인 및 보강해줘.
```
