# Next Session

## 세션 목표
- `OLLAMA_PLAN.md` Phase 2(Bounded Execution) 본 작업: `agents/coder.py`가 `LLMFactory`를 사용하도록 리팩토링하고, 로컬 모델(Ollama) 기반의 단순 코드 구현 능력을 실험한다.

## 컨텍스트
- Phase 1(Memory)과 TUI 인프라가 모두 안정화되었습니다.
- 이제 실제 작업자 에이전트인 `Coder`가 Gemini의 값비싼 추론 대신 로컬 모델을 활용하여 간단한 함수 작성이나 리팩토링을 수행할 수 있는지 검증해야 합니다.

## 범위 (Scope)
### 수행할 작업 (Do)
- `agents/coder.py`: `GortexAuth`를 `LLMFactory.get_default_backend()`로 교체.
- **Capability-based Logic**: 백엔드가 `supports_structured_output()`을 지원하지 않을 경우(Ollama), JSON Schema 대신 프롬프트 지시 및 텍스트 파싱 전략으로 자동 전환하는 로직 구현.
- **Fallback Strategy**: 로컬 모델의 출력이 파싱 불가능하거나 품질이 낮을 경우 자동으로 Gemini로 재시도하는 회복 로직 구현.
- `tests/test_coder.py`: 새로운 백엔드 주입 구조에 맞춰 테스트 코드 수정.

### 수행하지 않을 작업 (Do NOT)
- `Manager`의 오케스트레이션 로직은 여전히 Gemini를 최우선으로 사용한다.
- 복잡한 다중 파일 수정 작업은 여전히 Gemini를 권장 모드로 유지한다.

## 기대 결과
- 단순 작업에 한해 로컬 모델을 사용함으로써 API 비용을 절감하고 오프라인 가용성을 높인다.
- 모델의 능력에 따라 동적으로 행동을 최적화하는 'Hybrid AI'의 정수를 구현한다.

## 완료 기준
- `Coder` 에이전트에서 `LLMFactory` 기반 백엔드 주입 완료.
- Ollama 시뮬레이션 환경에서 단순 코드 생성 성공.
- `docs/sessions/session_0062.md` 기록.
