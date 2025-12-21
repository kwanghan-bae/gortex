# Next Session

## 세션 목표
- `OLLAMA_PLAN.md` Phase 2(Bounded Execution) 진입: `utils/token_counter.py` 추상화 및 `agents/coder.py`의 부분적 로컬 모델 도입을 준비한다.

## 컨텍스트
- Phase 1(Memory 압축) 구현이 완료되어 로컬 모델 활용의 첫 단추를 끼웠습니다.
- 이제 토큰 계산 로직(`token_counter.py`)이 특정 모델(Gemini)에 종속되지 않도록 개선하고, 실제 작업자 에이전트(`Coder`)가 로컬 모델을 활용할 수 있는 구조를 검토해야 합니다.

## 범위 (Scope)
### 수행할 작업 (Do)
- `utils/token_counter.py`: `tiktoken` 등을 활용하거나 근사치 계산 로직을 도입하여 벤더 중립적인 인터페이스로 개선.
- `agents/coder.py`: 현재 `LLMBackend`를 사용하고 있지 않다면, 이를 사용하도록 리팩토링할 지점을 식별하고 구조 설계. (실제 적용은 위험도가 높으므로 설계 우선)
- `tests/test_token_counter.py`: 변경된 로직 검증.

### 수행하지 않을 작업 (Do NOT)
- `Coder`가 당장 로컬 모델로 코드를 짜게 만들지 않는다. (검증되지 않은 모델 성능으로 인한 코드 오염 방지)
- `Manager`의 판단 로직은 건드리지 않는다.

## 기대 결과
- 토큰 카운터가 모델에 상관없이 동작하는 일반적인 유틸리티로 진화한다.
- `Coder`의 LLM 전환을 위한 청사진이 마련된다.

## 완료 기준
- `utils/token_counter.py` 리팩토링 완료.
- `tests/test_token_counter.py` 통과.
- `docs/sessions/session_0060.md` 기록.
