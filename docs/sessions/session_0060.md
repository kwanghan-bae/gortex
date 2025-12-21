# Session 0060: Phase 2 진입 - Token Counter & Coder 설계

## 활동 요약
- **Token Counter Refactoring**: `utils/token_counter.py`를 리팩토링하여 특정 모델 API에 종속되지 않는 일반적인 근사치 계산 로직으로 전환했습니다. 특히 로컬 모델(Ollama) 사용 시 비용을 0으로 계산하도록 개선하여 하이브리드 운영의 비용 효율성을 반영했습니다.
- **LLM Capabilities**: `LLMBackend`에 `supports_structured_output` 및 `supports_function_calling` 메서드를 추가하여, 에이전트가 백엔드 능력에 따라 동적으로 전략(Native Tool vs Prompt Engineering)을 선택할 수 있는 기반을 마련했습니다.
- **Coder Design**: `agents/coder.py`에 `LLMFactory` 도입을 위한 설계 주석을 추가하고, 향후 Ollama 전환 시 고려해야 할 기술적 제약 사항(Schema 미지원 등)을 명시했습니다.

## 기술적 변경 사항
- **Utility**: `utils/token_counter.py`
    - `estimate_cost`: 모델명에 'qwen', 'llama' 등이 포함되면 비용 0 리턴.
    - `count_tokens`: 정규식 기반 근사치 계산 유지 (Backend Agnostic).
- **Core**: `core/llm/base.py` 및 구현체들
    - 기능 지원 여부 확인 메서드 추가.

## 테스트 결과
- `tests/test_token_counter.py`: 로컬 모델 비용(0.0) 테스트 케이스 추가 및 통과.
- `utils/token_counter.py` Coverage: 100%.
