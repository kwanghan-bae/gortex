# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** TrendScout & Workflow Graph Implemented

## 🧠 Current Context
모든 에이전트와 이들을 연결하는 `StateGraph`(`core/graph.py`)가 준비되었습니다.
이제 시스템을 실제로 구동하고 화려한 대시보드를 보여줄 **`main.py`**와 **`ui/dashboard.py`**를 완성해야 합니다.

## 🎯 Next Objective
**System Launch & UI Phase**
1. `gortex/ui/dashboard.py`: Rich 라이브러리를 사용하여 실시간 에이전트 상태 및 로그를 보여주는 대시보드 레이아웃 구현.
2. `gortex/main.py`: 사용자 입력을 받고 컴파일된 그래프를 실행하는 엔트리 포인트 구현.
   - `AsyncSqliteSaver`를 통한 세션 영속성 확보.
3. `core/observer.py`: 에이전트의 사고 과정을 구조화된 로그로 남기는 옵저버 구현.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 에이전트 워크플로우 그래프 완성.
- 다음 목표: `main.py` 및 `ui/dashboard.py` 구현.

주의사항:
- 대시보드는 Rich의 `Live`와 `Layout`을 활용하여 메인 채팅과 사이드바(상태창)를 구분할 것.
- `main.py`에서는 사용자가 `exit`를 입력할 때까지 루프를 돌며, 중단 시 체크포인트를 저장해야 함.
```
