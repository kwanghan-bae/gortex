# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** User Interruption & Manual Summary Ready (v1.2.7)

## 🧠 Current Context
시스템의 제어권이 사용자에게 더 많이 부여되었습니다. 이제 에이전트가 예상치 못한 방향으로 작업을 수행할 때 즉시 중단할 수 있으며, 필요에 따라 대화 내용을 강제로 요약하여 컨텍스트를 정리할 수 있습니다.

## 🎯 Next Objective
**Table Detection Refinement & Dynamic Thresholds**
1. **`Table Detection` Refinement**: `utils/table_detector.py`에서 불규칙한 공백이나 특수 문자가 섞인 텍스트 테이블을 더 유연하게 감지하도록 정규식을 보강합니다.
2. **`Dynamic Summarization`**: 현재 12개 메시지 고정인 요약 임계치를 현재 사용된 토큰량(Input context)에 따라 유동적으로 조절하는 로직을 검토합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 사용자 중단 및 수동 요약 명령어 추가 완료 (v1.2.7).
- 다음 목표: 테이블 감지 로직 정교화 및 동적 요약 임계치 도입.

작업 목표:
1. `utils/table_detector.py`의 정규식을 개선하여, 단일 공백으로만 구분된 테이블이나 양 끝에 공백이 불규칙한 행도 최대한 표로 인식하도록 해줘.
2. `core/graph.py`에서 `route_manager`의 요약 조건에 현재 메시지의 총 토큰 합계를 체크하는 로직을 추가하여, 12개가 안 되더라도 토큰이 너무 많으면 요약하도록 개선해줘.
```