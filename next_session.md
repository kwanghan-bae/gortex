# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Code Reviewer & Quality Scoring Complete (v1.8.4)

## 🧠 Current Context
코드 품질 측정 및 리뷰 시스템이 구축되었습니다. 이제 Gortex는 기능적인 완성도를 넘어 코드의 가독성, 유지보수 용이성까지 스스로 평가하고 개선할 수 있는 '품질 관리 지능'을 갖추게 되었습니다.

## 🎯 Next Objective
**GitHub Agent (Issue & PR Automation)**
1. **`Issue Analysis`**: 지정된 GitHub 저장소의 오픈된 이슈를 읽어와 작업 우선순위를 정하고 에이전트에게 할당합니다.
2. **`PR Creation`**: 작업이 완료되면 자동으로 브랜치를 생성하고, 변경 내역 요약과 함께 GitHub Pull Request를 생성하는 자동화 파이프라인을 구축합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 코드 리뷰 및 품질 점수화 완료 (v1.8.4).
- 다음 목표: GitHub 이슈 및 PR 자동화(GitHub Agent).

작업 목표:
1. `utils/git_tool.py`를 확장하여 GitHub API를 통한 이슈 조회 및 PR 생성 기능을 추가해줘.
2. `agents/manager.py`에서 저장소 링크가 주어지면 이슈를 분석하여 작업을 배분하는 지침을 보강해줘.
```