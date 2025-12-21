# Session 0062: Coder 에이전트 하이브리드 LLM 적용 (Phase 2)

## 활동 요약
- `agents/coder.py`를 리팩토링하여 `LLMFactory` 기반의 하이브리드 백엔드 구조를 도입했습니다.
- **Ollama Support**: Native Function Calling이나 Structured Output을 지원하지 않는 로컬 모델을 위해, 프롬프트 기반의 JSON 출력 강제 전략과 정규식 기반 응답 파싱 로직을 구현했습니다.
- **Dynamic Strategy**: 백엔드의 능력(`supports_structured_output`)에 따라 Gemini 전용 설정(`GenerateContentConfig`)과 일반 텍스트 설정을 동적으로 선택하도록 개선했습니다.
- **Robust Parsing**: 모델의 응답에서 JSON 블록을 추출하는 로직을 추가하여 Ollama 모델의 서술형 텍스트 포함 시에도 안정적인 파싱이 가능하게 했습니다.

## 기술적 변경 사항
- **Agent**: `agents/coder.py`
    - `GortexAuth` -> `LLMFactory.get_default_backend()`
    - `re` 모듈을 활용한 JSON 추출 로직 도입.
    - 가상 Function Call 객체 생성을 통한 기존 도구 실행 흐름과의 호환성 유지.
- **Testing**: `tests/test_coder.py`
    - Mock Backend를 활용하여 Ollama 시나리오(JSON 텍스트 응답) 검증.

## 테스트 결과
- `tests/test_coder.py` 통과.
- `agents/coder.py` 커버리지 확인 및 하이브리드 로직 보호.
