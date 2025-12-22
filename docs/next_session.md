# Next Session

## Session Goal
- **Local LLM Performance Optimization (Ollama Integration)**: 클라우드 API 할당량 소진 시에도 시스템이 원활하게 동작할 수 있도록, 로컬 모델(Ollama)의 추론 속도와 파싱 정확도를 최적화한다.

## Context
- `Session 0084`에서 클라우드 API 429 에러로 인해 실제 문서 치유가 지연됨.
- Gortex의 지속 가능성을 위해 로컬 모델은 단순한 백업이 아닌 '대등한 동료'로 성장해야 함.
- 현재 Ollama 연동은 되어 있으나, Structured Output(JSON) 파싱 안정성 및 복잡한 작업 수행 능력이 클라우드 모델 대비 낮음.

## Scope
### Do
- `core/llm/ollama_client.py`: Ollama 모델의 프롬프트 템플릿 최적화 (ChatML 포맷 등 적용).
- `core/llm/factory.py`: 할당량 소진 감지 시 즉시 로컬 모델로 전환하는 스마트 폴백 로직 강화.
- `utils/tools.py`: 로컬 모델의 출력을 위한 전용 JSON 복구(Healing) 알고리즘 구현.

### Do NOT
- 대규모 모델 학습(Fine-tuning)은 진행하지 않음 (기존 모델의 효율적 사용에 집중).

## Expected Outputs
- `core/llm/ollama_client.py` (Update)
- `core/llm/factory.py` (Update)
- `utils/tools.py` (Update)

## Completion Criteria
- 클라우드 API를 강제로 차단했을 때, Ollama를 통해 `GortexState` 구조 분석 및 JSON 파싱이 100% 성공해야 함.
- `docs/sessions/session_0085.md` 기록.
