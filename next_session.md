# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Table Detection Polish & UI Progress Complete (v1.4.4)

## 🧠 Current Context
시스템의 시각적 완성도와 데이터 파싱 능력이 정점에 가까워지고 있습니다. 이제 대시보드는 거의 모든 형태의 표 데이터를 정확히 렌더링하며, 도구 실행 시 진행 상태를 더 역동적으로 보여줍니다.

## 🎯 Next Objective
**Concurrency Refinement & Real-world Usage**
1. **`Background Execution`**: Researcher와 같이 외부 API나 브라우저를 사용하는 도구들이 실행되는 동안에도 UI가 부드럽게 유지되도록 비동기 처리(asyncio)의 세밀한 구간을 튜닝합니다.
2. **`Adaptive Throttling`**: `429 Quota Exhausted` 에러가 자주 발생할 경우, 시스템이 스스로 사고의 깊이나 도구 사용 횟수를 일시적으로 제한하는 '능동적 스로틀링' 로직을 구상합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 테이블 파싱 및 진행 바 UI 고도화 완료 (v1.4.4).
- 다음 목표: 비동기 처리 튜닝 및 능동적 스로틀링 구상.

작업 목표:
1. `agents/researcher.py`에서 대규모 검색 수행 시 UI 갱신이 밀리지 않도록 `asyncio.sleep`을 적절히 주입하여 제어권을 양보해줘.
2. `core/auth.py`에 최근 1분간의 API 호출 횟수를 카운트하는 로직을 추가하고, 임계치에 도달하면 `Optimizer`에게 알리는 기반을 마련해줘.
```