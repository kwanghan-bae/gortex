# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Architecture Sketcher & Mermaid Integration Complete (v1.7.7)

## 🧠 Current Context
아키텍처 스케쳐 기능이 도입되어 이제 Planner는 복잡한 시스템 구조를 Mermaid 다이어그램으로 시각화할 수 있습니다. 이 데이터는 실시간으로 웹 대시보드에 스트리밍되어 사용자가 설계 의도를 직관적으로 파악할 수 있게 돕습니다.

## 🎯 Next Objective
**Mental Sandbox (Pre-Action Simulation)**
1. **`Action Simulation`**: 에이전트가 `write_file`이나 `execute_shell`과 같은 파괴적인 도구를 호출하기 전, 예상되는 결과와 위험 요소를 미리 '상상(Simulate)'하는 단계를 추가합니다.
2. **`Safety Guard`**: 시뮬레이션 결과 시스템에 치명적인 위해를 가할 가능성이 있다면, 에이전트 스스로 실행을 취소하고 대안을 찾도록 하는 '심적 샌드박스' 로직을 구축합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 아키텍처 다이어그램 시각화 기능 완료 (v1.7.7).
- 다음 목표: 도구 실행 전 사전 시뮬레이션(Mental Sandbox).

작업 목표:
1. `agents/coder.py`의 `response_schema`에 `simulation_result` 필드를 추가하여 도구 호출 전 예상 결과를 서술하도록 해줘.
2. `Mental Sandbox` 규칙을 지침에 추가하여, 위험한 명령어가 감지되면 스스로 거부하거나 안전한 대안을 제시하도록 로직을 보강해줘.
```
