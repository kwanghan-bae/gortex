# Release Notes

## [Unreleased]

### v2.8.5 (2025-12-23)
- **Feature**: LM Studio 연동을 위한 `LMStudioBackend` 구현. `LLM_BACKEND` 환경 변수를 통해 로컬 모델 백엔드를 선택할 수 있으며, 하이브리드 모드 시 Gemini/Ollama 실패 시 자동 폴백합니다.
- **Quality**: 프로젝트 전반에 걸쳐 400개 이상의 린트 에러(복수 구문, 미사용 변수, 잘못된 예외 처리 등)를 수정하여 코드 베이스의 건전성을 대폭 강화했습니다.
- **Testing**: `utils/tools.py`, `utils/economy.py`, `core/auth.py` 등 주요 모듈에 대한 유닛 테스트를 보강하여 커버리지를 확대했습니다.
- **Bug Fix**: `core/auth.py`에서 `get_current_client` 메서드 부재로 인한 벡터 스토어 오류를 수정했습니다.

## Completed

### v2.8.4 (Hybrid Coder & Bounded Execution)
- **Agent**: `agents/coder.py`에 하이브리드 LLM 아키텍처를 적용하여 Gemini와 Ollama를 모두 지원하게 되었습니다.
- **Strategy**: 모델의 Native 기능 지원 여부에 따라 프롬프트 전략과 도구 호출 방식(Native vs Simulated)을 동적으로 전환합니다.
- **Resilience**: 정규식 기반 JSON 추출 로직을 도입하여 로컬 모델의 비정형 응답에 대한 파싱 신뢰도를 높였습니다.

# ... (Previous notes omitted for brevity)
