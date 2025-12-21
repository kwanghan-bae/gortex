# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** State Merger & Conflict Resolution Complete (v1.9.1)

## 🧠 Current Context
병렬 작업(Swarm) 결과의 상태 병합 로직이 안착되었습니다. 이제 여러 에이전트가 동시에 지식을 수집하거나 파일을 분석하더라도, 그 결과물이 유실 없이 메인 시스템의 맥락으로 통합됩니다.

## 🎯 Next Objective
**Resource Monitor & Dashboard Polish**
1. **`Resource Monitoring`**: 시스템의 실시간 리소스 사용량(CPU, RAM)과 현재 활성화된 에이전트들의 부하를 측정하는 백그라운드 태스크를 구현합니다.
2. **`Visual Monitor`**: 웹 대시보드에 실시간 그래프 위젯을 추가하여, Gortex가 현재 얼마나 많은 연산 자원을 사용하고 있는지 시각적으로 모니터링할 수 있게 합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 병렬 작업 결과 병합 및 충돌 해결 완료 (v1.9.1).
- 다음 목표: 실시간 리소스 모니터링 시스템 구축.

작업 목표:
1. `utils/resource_monitor.py`를 신설하여 시스템 자원(psutil 활용 등)을 측정하는 기초 로직을 작성해줘.
2. `ui/web_server.py`를 통해 측정된 리소스 데이터를 웹 대시보드로 실시간 브로드캐스팅하도록 연동해줘.
```
