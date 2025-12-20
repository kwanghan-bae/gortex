# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Thought Log Persistence Complete (v1.5.7)

## 🧠 Current Context
세션 스냅샷에 에이전트의 사고 과정이 포함되었습니다. 이제 작업을 불러올 때 에이전트가 어떤 고민을 하며 현재 상태에 도달했는지 시각적으로 확인할 수 있어 연속성 있는 작업이 가능합니다.

## 🎯 Next Objective
**Multi-LLM Resilience (Fallback Bridge)**
1. **`Fallback Engine`**: `GortexAuth` 엔진을 확장하여 Gemini API 할당량이 모두 소진되거나 오류가 발생할 경우, `.env`에 설정된 OpenAI 또는 Anthropic 키를 사용하여 즉시 대체 모델로 전환하는 기능을 구현합니다.
2. **`Model Mapping`**: 각 에이전트가 사용하는 모델(`flash`, `pro` 등)에 대응하는 타사 모델 매핑 테이블을 구축합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 사고 과정 포함 세션 스냅샷 구현 완료 (v1.5.7).
- 다음 목표: 멀티 LLM 폴백 브리지 구축.

작업 목표:
1. `core/auth.py`의 `GortexAuth` 클래스에 OpenAI/Anthropic 지원을 위한 기초 로직을 추가해줘.
2. `generate` 메서드에서 Gemini 실패 시 다른 제공업체로 전환하는 `switch_provider` 로직을 구현해줘.
```
