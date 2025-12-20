# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Multi-LLM Fallback Bridge Complete (v1.5.8)

## 🧠 Current Context
멀티 LLM 폴백 브리지가 완성되었습니다. 이제 Gemini API 할당량이 소진되더라도 시스템은 중단 없이 OpenAI(GPT-4o)로 자동 전환되어 작업을 이어갈 수 있습니다.

## 🎯 Next Objective
**LLM Provider Status UI**
1. **`Provider Visualization`**: 대시보드 사이드바의 `SYSTEM STATUS` 패널에 현재 사용 중인 LLM 제공업체(Gemini 또는 OpenAI) 정보를 실시간으로 표시합니다.
2. **`Quota Monitoring`**: 최근 1분간의 API 호출 횟수를 시각적으로 그래프나 바 형태로 표시하여 스로틀링 임계치에 도달했는지 직관적으로 알 수 있게 합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 멀티 LLM 폴백 브리지 구축 완료 (v1.5.8).
- 다음 목표: LLM 제공업체 상태 및 할당량 시각화.

작업 목표:
1. `ui/dashboard.py`의 `update_sidebar` 메서드를 수정하여 현재 활성화된 LLM 제공업체(`GortexAuth._provider`)를 표시해줘.
2. `STATUS` 패널에 최근 1분간의 API 호출 빈도를 바(Bar) 형태로 시각화해줘.
```