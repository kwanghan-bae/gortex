# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Context Optimization & UI Polish Complete (v1.3.4)

## 🧠 Current Context
시스템의 운영 효율성과 시각적 역동성이 강화되었습니다. 이제 대화가 길어질수록 더 지능적으로 압축을 수행하며, 대시보드 UI는 현재 누가 작업 중인지 테두리 색상 변화를 통해 직관적으로 알려줍니다.

## 🎯 Next Objective
**Detailed Observation & API Resilience**
1. **`Observation Highlight`**: 도구 실행 결과(`Observation`) 패널에 `Rich.Syntax`를 적용할 때, 파일 확장자나 내용을 분석하여 더 정확한 언어로 하이라이팅되도록 개선합니다.
2. **`Quota Resilience`**: 모든 API 키가 소진되었을 때, 프로그램이 단순히 종료되는 것이 아니라 사용자에게 즉시 알리고 키 수동 입력을 유도하거나 대기 시간을 제안하는 로직을 구체화합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 동적 압축 및 사이드바 테두리 색상 연동 완료 (v1.3.4).
- 다음 목표: 도구 결과 시각화 정밀화 및 키 소진 대응 강화.

작업 목표:
1. `ui/dashboard.py`에서 `tool` 메시지 렌더링 시, `content`의 내용을 보고 언어(python, json, shell, sql 등)를 더 똑똑하게 판별하여 Syntax 하이라이팅을 적용해줘.
2. `main.py`에서 할당량 소진 에러 발생 시, 사용자에게 현재 상태를 설명하는 전용 레이아웃(Panel)을 보여준 뒤 종료하도록 보완해줘.
```
