# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Async Responsiveness & Auth Monitoring Complete (v1.4.5)

## 🧠 Current Context
시스템의 내부 모니터링과 UI 반응성이 더욱 정교해졌습니다. 이제 `Auth` 엔진은 자신의 활동 빈도를 스스로 감시하며, `Researcher`는 긴 작업을 수행하면서도 UI가 얼어붙지 않도록 제어권을 양보합니다.

## 🎯 Next Objective
**Adaptive Throttling & Advanced Logging**
1. **`Adaptive Throttling`**: `Auth`에서 감지한 호출 빈도가 임계치를 넘을 경우, `Manager`가 다음 태스크의 사고 깊이를 낮추거나(Flash-Lite 모델 강제 등) 잠시 대기하도록 유도하는 능동적 부하 조절 로직을 구현합니다.
2. **`Log Persistence`**: `trace.jsonl` 로그 파일이 너무 커질 경우를 대비해, 일정 용량 초과 시 자동으로 롤링(Rolling)하거나 압축 보관하는 유틸리티를 추가합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- API 호출 모니터링 및 비동기 반응성 개선 완료 (v1.4.5).
- 다음 목표: 능동적 스로틀링 및 로그 로테이션 구현.

작업 목표:
1. `core/auth.py`의 호출 빈도 정보를 `state`에 포함시켜, `Manager`가 이를 보고 지능적으로 모델을 선택(Flash -> Flash-Lite)하도록 로직을 보강해줘.
2. `core/observer.py`에 로그 파일 크기를 체크하여 10MB 초과 시 `.bak`으로 옮기는 간단한 로그 로테이션 기능을 추가해줘.
```
