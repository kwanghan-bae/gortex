# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Adaptive Throttling & Log Rotation Complete (v1.4.6)

## 🧠 Current Context
시스템의 자기 보호 능력과 로그 관리 효율성이 강화되었습니다. 이제 Gortex는 API 사용량이 많아지면 스스로 가벼운 모델로 전환하여 비용과 할당량을 아끼며, 로그 파일의 무한 증식을 방지하는 로테이션 기능을 갖추었습니다.

## 🎯 Next Objective
**Visual Sophistication & System Resilience**
1. **`Background Progress`**: 도구 실행(특히 Researcher) 중에도 대시보드 UI가 부드럽게 유지되도록 비동기 구조를 더욱 세밀하게 튜닝합니다.
2. **`Self-Correction Manual`**: Coder 에이전트가 흔히 저지르는 실수(IndentationError 등)에 대한 '자가 수정 가이드'를 프롬프트에 더 구체적인 사례(Few-shot)로 추가하여 수리 속도를 높입니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 능동적 스로틀링 및 로그 로테이션 완료 (v1.4.6).
- 다음 목표: UI 반응성 최적화 및 Coder 자가 수정 지능 강화.

작업 목표:
1. `ui/dashboard.py`에서 에이전트 전환이나 도구 실행 시 사이드바 패널의 타이틀 색상이 함께 변하도록 스타일링을 정밀화해줘.
2. `agents/coder.py`의 시스템 프롬프트에 'Python 구문 오류(Syntax/Indent) 해결을 위한 3단계 체크리스트'를 추가해줘.
```