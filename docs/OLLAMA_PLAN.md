# 📡 Gortex Ollama-based Local Model Expansion Plan

**Status:** Phase 0 (Design Locked / Documentation Only)
**Core Concept:** "Ollama is how Gortex works longer, not how Gortex thinks better."

---

## 1. Core Principles

1.  **Non-Negotiable Continuity**: Ollama 도입이 현재의 워크플로우나 자동화 계약을 깨뜨려서는 안 된다.
2.  **Stateless First**: 로컬 모델을 사용하더라도 모든 맥락은 파일(Repository)에 기록되어야 한다.
3.  **Worker vs Manager**: Ollama는 반복적이고 정의된 작업(Worker)을 수행하며, 고수준의 설계와 라우팅은 여전히 고성능 외부 모델(Manager)이 담당한다.

---

## 2. Phased Rollout Roadmap

### 🟦 Phase 1: Utility Tasks (Read-Only)
*   **Target**: 로그 요약, 컨텍스트 압축(`memory.py`), 효율성 점수 계산.
*   **Rule**: 파일 수정이나 셸 실행 권한 없음. 결과는 조언용으로만 사용.
*   **Fallback**: Ollama 실패 시 즉시 Gemini로 자동 재시도.

### 🟨 Phase 2: Bounded Execution (Workers)
*   **Target**: `Coder` (루프 내 단순 구현), `Optimizer` (성능 튜닝 제안).
*   **Constraint**: Planner가 수립한 명시적 계획 하에서만 작동. 신규 파일 생성 및 문서 수정 금지.

### 🟥 Phase 3: Isolated Autonomous Loops
*   **Target**: 장기 실행 진화 실험.
*   **Environment**: 메인 저장소와 격리된 샌드박스에서 구동.

---

## 3. Configuration Plan

`.env` 파일에 다음 항목이 추가될 예정이다 (Phase 1 가동 시).
```ini
LLM_BACKEND=gemini        # gemini | ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=qwen2.5-coder:7b
```
