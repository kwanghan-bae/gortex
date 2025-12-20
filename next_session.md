# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Few-shot Evolution & Markdown Tables Complete (v1.2.6)

## 🧠 Current Context
시스템의 추출 능력과 시각화 능력이 한층 강화되었습니다. `Analyst`는 이제 구체적인 예시를 통해 더 정확한 규칙을 만들어내며, 대시보드는 Markdown 스타일의 표도 깔끔하게 렌더링할 수 있습니다.

## 🎯 Next Objective
**User Interruption & Context Management**
1. **`Interruption` Refinement**: 에이전트가 긴 답변을 하거나 복잡한 작업을 수행 중일 때, 사용자가 특정 입력을 통해 안전하게 중단하고 즉시 새로운 지시를 내릴 수 있는 흐름을 정교화합니다.
2. **`Summarizer` Threshold**: 현재 12개 메시지 고정인 요약 임계치를 토큰 사용량에 따라 동적으로 조절하거나, 사용자가 원할 때 수동으로 요약(` /summarize`)하는 기능을 추가합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- Few-shot 규칙 추출 및 Markdown 테이블 지원 완료 (v1.2.6).
- 다음 목표: 사용자 중단 루틴 및 요약 로직 고도화.

작업 목표:
1. `main.py`의 실행 루프에서 에이전트 스트리밍 중 `Ctrl+C` 감지 시 즉시 현재 단계를 중단하고 `manager` 노드로 제어권을 넘기는 예외 처리 로직을 강화해줘.
2. `/summarize` 명령어를 추가하여 사용자가 원할 때 즉시 `summarizer` 노드를 호출할 수 있게 해줘.
```
