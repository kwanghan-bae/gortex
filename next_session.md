# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Performance Profiler & Cost Analysis Complete (v1.7.4)

## 🧠 Current Context
성능 프로파일러가 도입되어 이제 Gortex의 모든 행동은 시간과 비용의 관점에서 정밀하게 기록됩니다. 이 데이터를 통해 어떤 노드가 병목을 일으키는지, 비용 효율적인 모델 선택이 이루어지고 있는지 분석할 수 있는 토대가 마련되었습니다.

## 🎯 Next Objective
**Visual Latency & Cost Tracking UI**
1. **`Performance Dashboard`**: 대시보드 사이드바에 현재 세션의 '평균 지연 시간'과 '누적 토큰 비용'을 더 눈에 띄게 시각화합니다.
2. **`Response Time Alert`**: 특정 노드의 응답 속도가 비정상적으로 느려질 경우(예: > 10s), 사용자에게 시각적 경고를 보내거나 에이전트 스스로 최적화 모드로 전환하도록 유도합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 성능 프로파일링 및 비용 기록 기능 구현 완료 (v1.7.4).
- 다음 목표: 실시간 지연 시간 및 비용 추적 UI 고도화.

작업 목표:
1. `ui/dashboard.py`의 `update_sidebar` 메서드를 수정하여 'Avg Latency' 정보를 추가로 표시해줘.
2. `main.py`에서 누적된 레이턴시 데이터를 계산하여 UI에 전달하는 로직을 보강해줘.
```