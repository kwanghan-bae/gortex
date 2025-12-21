# Next Session

## 세션 목표
- `core/llm` 추상화 계층을 실제 유틸리티(`utils/memory.py` 등)에 적용하여 Phase 1(Read-Only Tasks)을 완성한다.

## 컨텍스트
- 지난 세션에서 `core/llm/` 인프라를 구축하여 Gemini와 Ollama를 선택적으로 사용할 수 있게 되었습니다.
- 이제 실제 에이전트나 유틸리티가 이 추상화 계층을 사용하도록 리팩토링하여 로컬 모델의 효용성을 증명해야 합니다.

## 범위 (Scope)
### 수행할 작업 (Do)
- `utils/memory.py`: 직접적인 `GortexAuth` 의존성을 제거하고 `LLMFactory.get_backend()`를 사용하도록 리팩토링.
- `utils/token_counter.py`: 토큰 계산 로직이 로컬 모델의 토크나이저(또는 근사치)를 고려하도록 개선 검토.
- `core/llm/ollama_client.py`: 실제 Ollama 서버가 없을 때의 Graceful Fallback(자동 Gemini 전환) 로직 보강.
- `tests/test_memory.py`: 리팩토링된 코드가 기존 테스트를 통과하는지 확인 및 Ollama 백엔드에서의 동작 검증.

### 수행하지 않을 작업 (Do NOT)
- 핵심 에이전트(Manager, Coder)는 여전히 Gemini를 사용하도록 유지한다 (Phase 2 전까지).
- 무거운 모델(`qwen2.5-coder` 등)을 강제로 다운로드하거나 실행하는 자동화 스크립트는 포함하지 않는다 (사용자 환경 존중).

## 기대 결과
- 메모리 압축(`compress_synapse`) 작업이 로컬 Ollama 모델을 통해 수행될 수 있다.
- 외부 API 장애 시에도 로컬 모델이 백업으로 동작하는 초기적 회복 탄력성을 확보한다.

## 완료 기준
- `utils/memory.py`의 `GortexAuth` import 제거.
- `tests/test_memory.py` 통과 및 커버리지 유지.
- `docs/sessions/session_0059.md` 기록.