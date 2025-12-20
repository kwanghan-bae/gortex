# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Cache Concurrency & Display Optimization Complete (v1.3.7)

## 🧠 Current Context
시스템의 안정성과 UI 반응성이 더욱 견고해졌습니다. 파일 캐시 업데이트가 안전하게 통합되었으며, 대시보드는 많은 양의 대화가 쌓여도 가독성을 잃지 않도록 최적화되었습니다.

## 🎯 Next Objective
**Intelligence & Robustness Refinement**
1. **`Auto-Correction` Refinement**: `Coder` 에이전트가 `execute_shell` 실패 시 `stderr`를 보고 스스로 수정하는 루프를 더 지능적으로 만들기 위해, 일반적인 에러 메시지(ModuleNotFoundError 등)에 대한 '즉각적인 해결 라이브러리'를 프롬프트에 사례로 추가합니다.
2. **`Background Tools`**: 시간이 오래 걸리는 도구(예: 대규모 검색 또는 긴 테스트) 실행 시 UI가 완전히 멈추지 않도록 비동기 처리를 더 정교하게 다듬습니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 캐시 정합성 및 UI 최적화 완료 (v1.3.7).
- 다음 목표: Coder 자가 수정 지능 강화 및 도구 실행 비동기성 고도화.

작업 목표:
1. `agents/coder.py`의 시스템 프롬프트에 'Python 에러 코드별 표준 대응 매뉴얼'을 숏컷 형태로 추가하여, 에러 발생 시 더 빠르게 코드를 수정하도록 해줘.
2. `main.py`에서 `app.astream` 실행 중 UI 업데이트가 더 매끄럽게 되도록 `asyncio.sleep` 위치와 갱신 주기를 최적화해줘.
```