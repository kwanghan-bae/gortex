# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Synaptic Indexing Engine Complete (v1.6.0)

## 🧠 Current Context
프로젝트의 코드 구조를 정적으로 분석하여 인덱싱하는 엔진이 구축되었습니다. 이제 시스템은 어떤 파일에 어떤 클래스와 함수가 있는지 알고 있으며, 이를 통해 대규모 코드베이스에서도 길을 잃지 않고 작업을 수행할 수 있는 준비가 되었습니다.

## 🎯 Next Objective
**Context-Aware Reasoning (Index Injection)**
1. **`Context Injection`**: 에이전트가 코드를 수정하거나 분석할 때, 인덱싱된 정보를 바탕으로 관련 있는 코드 정의(클래스/함수 시그니처)를 프롬프트에 자동으로 주입합니다.
2. **`Ambiguity Resolution`**: 사용자가 "GortexAuth 고쳐줘"라고 했을 때, 인덱스 검색을 통해 즉시 `core/auth.py`의 위치를 파악하고 해당 클래스 구조를 읽어오는 지능형 라우팅을 구현합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- AST 기반 코드 인덱싱 엔진 구축 완료 (v1.6.0).
- 다음 목표: 인덱스 정보를 활용한 지능형 코드 맥락 인식.

작업 목표:
1. `agents/coder.py` 또는 `agents/planner.py`에서 `SynapticIndexer`의 검색 결과를 활용하여 필요한 코드 정의를 미리 읽어오는 로직을 추가해줘.
2. 에이전트가 파일 경로를 명시적으로 알지 못해도 심볼명(클래스/함수명)만으로 작업을 시작할 수 있도록 'Symbol-to-Path' 해결 기능을 강화해줘.
```