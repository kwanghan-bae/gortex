# ⏭️ Gortex Next Session Context

**Date:** 2024-12-21
**Status:** Natural Language Macro Complete (v2.2.18)

## 🧠 Current Context
시스템은 매크로를 통해 사용자의 워크플로우를 학습합니다. 이제 프로젝트의 건강 상태를 더 깊이 파악하기 위해, 코드베이스 전체의 복잡도(Complexity)를 시각화하여 기술 부채(Technical Debt)가 쌓인 곳을 알려주는 기능이 필요합니다.

## 🎯 Next Objective
**Code Complexity Heatmap (Technical Debt Visualization)**
1. **`Complexity Scanner`**: `agents/analyst.py`가 프로젝트 내 모든 소스 코드를 스캔하여 파일별 사이클로매틱 복잡도(Cyclomatic Complexity)를 계산하고 점수화합니다.
2. **`Debt Dashboard`**: 가장 복잡도가 높은 상위 5개 파일과 점수를 대시보드(터미널/웹)에 'Technical Debt' 패널로 시각화합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 매크로 기능 구현 완료 (v2.2.18).
- 다음 목표: 코드 복잡도 히트맵 시각화.

작업 목표:
1. `agents/analyst.py`에 `scan_project_complexity` 메서드를 추가하여 전체 파일의 복잡도를 계산해줘 (외부 라이브러리 `radon` 사용 시도, 없으면 간단한 분기문 카운팅 로직 사용).
2. `main.py`에서 주기적으로(또는 `/scan_debt` 명령어로) 이 메서드를 호출하고, 결과를 `ui.update_debt_panel`로 전달해줘.
3. `ui/dashboard.py`에 `Technical Debt` 패널을 추가해줘.
```