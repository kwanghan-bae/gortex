# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Deep Integrity Check & Cache Healing Complete (v1.7.3)

## 🧠 Current Context
시스템 부팅 시 프로젝트의 모든 파일을 전수 조사하여 캐시와의 무결성을 검증하는 엔진이 안착되었습니다. 이제 외부에서 파일이 수정되거나 삭제되더라도 Gortex는 이를 즉시 인지하고 지식 베이스를 동기화할 수 있습니다.

## 🎯 Next Objective
**Performance Profiler & Cost Analysis**
1. **`Performance Profiler`**: 에이전트의 도구 호출 시간, 성공률, 토큰 사용 비용을 노드별로 정밀 측정하여 `trace.jsonl`에 기록합니다.
2. **`Optimization Recommendations`**: 분석된 데이터를 바탕으로, 특정 작업에 너무 많은 비용이 들거나 지연 시간이 길어질 경우 `Optimizer`가 더 가벼운 모델로 전환하거나 도구 호출 방식을 변경하도록 제안하는 기능을 구현합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 파일 캐시 정밀 무결성 검증 완료 (v1.7.3).
- 다음 목표: 성능 프로파일러 및 비용 분석 엔진 구축.

작업 목표:
1. `core/observer.py`를 확장하여 각 노드 실행 시 소요 시간과 상세 토큰 비용(입력/출력 구분)을 측정하는 프로파일링 로직을 작성해줘.
2. `main.py` 또는 `ui/dashboard.py`에서 실시간으로 누적 비용과 평균 지연 시간을 표시하는 위젯 기능을 보강해줘.
```
