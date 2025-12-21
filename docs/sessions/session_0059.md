# Session 0059: Memory 모듈 LLM 추상화 적용 (Phase 1 구현)

## 활동 요약
- `utils/memory.py`가 더 이상 `GortexAuth`(Gemini 전용)에 직접 의존하지 않도록 리팩토링했습니다.
- `core/llm/factory.py`를 통해 백엔드를 주입받음으로써, 환경 변수(`LLM_BACKEND=ollama`) 설정만으로 로컬 모델을 사용하여 컨텍스트 압축이 가능해졌습니다.
- **Dynamic Model Selection**: 백엔드가 Ollama일 경우 `OLLAMA_DEFAULT_MODEL` 환경 변수 값을 사용하여 모델을 유연하게 선택하도록 로직을 개선했습니다.
- **Message Normalization**: `utils/memory.py` 내부에서 메시지 포맷(Tuple/Dict)을 `LLMBackend`가 요구하는 List[Dict] 형태로 자동 변환하는 어댑터 로직을 추가했습니다.

## 기술적 변경 사항
- **Refactoring**: `utils/memory.py`
    - Removed: `from gortex.core.auth import GortexAuth`
    - Added: `from gortex.core.llm.factory import LLMFactory`
    - Logic: `compress_synapse` 함수가 팩토리를 통해 백엔드를 획득하고, `google.genai.types` 설정 객체 대신 표준 Dictionary 설정을 사용합니다.

## 테스트 결과
- `tests/test_memory.py`: Mocking 대상을 `GortexAuth`에서 `LLMFactory`로 변경하고, Ollama 환경 변수 시나리오 테스트를 추가했습니다.
- **Coverage**: `utils/memory.py` 100% 달성.
