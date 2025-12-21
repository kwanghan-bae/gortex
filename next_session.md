# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** GitHub Agent & PR Automation Complete (v1.8.5)

## 🧠 Current Context
GitHub API 연동이 완료되어 이제 Gortex는 이슈 분석부터 코드 수정, 그리고 최종 PR 생성까지 이어지는 전체 개발 사이클을 자동화할 수 있습니다. 이는 협업 환경에서 Gortex의 독립적인 기여 가능성을 열어줍니다.

## 🎯 Next Objective
**Live Documentation (Real-time API Search)**
1. **`Documentation Retrieval`**: 새로운 라이브러리나 생소한 API를 사용해야 할 때, 에이전트가 코드를 작성하기 전 구글 검색이나 공식 문서를 실시간으로 크롤링하여 최신 사용법을 학습합니다.
2. **`Context Enrichment`**: 검색된 최신 API 시그니처와 예제 코드를 Coder의 프롬프트에 주입하여, 할루시네이션(Hallucination)을 최소화하고 정확한 코드를 작성하도록 돕습니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- GitHub 연동 및 자동 PR 기능 완료 (v1.8.5).
- 다음 목표: 실시간 API 문서 검색 및 맥락 강화(Live Documentation).

작업 목표:
1. `agents/researcher.py`의 검색 기능을 고도화하여 특정 라이브러리의 최신 API 문서를 정밀하게 추출하는 `fetch_api_docs` 메서드를 추가해줘.
2. `coder`가 생소한 모듈을 다룰 때 자동으로 `researcher`를 호출하여 문서를 읽어오도록 워크플로우를 보강해줘.
```
