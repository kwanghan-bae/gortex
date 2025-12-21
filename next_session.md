# ⏭️ Gortex Next Session Context

**Date:** 2024-12-21
**Status:** Active Refactoring Proposal Complete (v2.2.16)

## 🧠 Current Context
시스템은 신기술을 감지하고 리팩토링을 제안하며, 효율성을 스스로 관리합니다. 이제 코드 품질의 핵심인 '테스트 자동화'를 강화해야 합니다. Coder가 기능을 구현할 때, 이에 상응하는 단위 테스트를 자동으로 생성하도록 강제하는 메커니즘이 필요합니다.

## 🎯 Next Objective
**Automated Test Generation (Quality Assurance v1)**
1. **`Test Mandate`**: `agents/planner.py`가 계획을 수립할 때, 신규 기능 구현 단계 직후에 반드시 '단위 테스트 작성(Write Unit Test)' 단계를 포함하도록 로직을 강화합니다.
2. **`Test-Driven Coder`**: `agents/coder.py`가 테스트 코드를 작성할 때, `unittest` 표준을 준수하고 기존 테스트 스위트와 호환되도록 프롬프트를 보강합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 리팩토링 제안 시스템 완료 (v2.2.16).
- 다음 목표: 단위 테스트 자동 생성 강제화.

작업 목표:
1. `agents/planner.py`에서 계획 생성 시, 코드를 수정하는 작업이 있다면 반드시 그에 따른 '테스트 코드 작성' 단계를 추가하도록 로직을 수정해줘.
2. `agents/coder.py`의 시스템 프롬프트에 `unittest` 기반의 테스트 코드 작성 가이드라인을 추가해줘.
```