# Next Session

## 세션 목표
- 80% 커버리지를 유지하며 `core/evolutionary_memory.py`와 `utils/memory.py`의 회귀/캐시 복원 경로를 테스트로 확보한다.

## 컨텍스트
- `tests/test_commands.py`/`tests/test_vector_store.py`를 통해 명령어 제어 및 벡터 기억 흐름을 확증했고, 전체 커버리지는 80%에 도달했습니다.
- 자동 반복 사이클(`coverage run -m pytest` → `coverage report`)은 계속되며, 문서(릴리즈 노트/세션 로그/next_session)가 매 사이클 변화를 기록합니다.

## 범위 (Scope)
### 수행할 작업 (Do)
- `core/evolutionary_memory.py`: 메모리 증식, 인과 기록, 실패 시 복원 로직을 Mock 기반으로 시뮬레이션하여 evolution 단계의 신뢰성을 검증한다.
- `utils/memory.py`: 임시/장기 메모리 병합, pruning, threshold 초과 로깅 및 캐시 버전 충돌 감지 흐름을 테스트로 포착한다.
- `coverage run -m pytest` → `coverage report` 사이클을 반복하고 문서(릴리즈 노트/세션 로그/next_session)를 갱신한다.

### 수행하지 않을 작업 (Do NOT)
- Web UI(React/Three.js) 또는 `ui/three_js_bridge.py`의 시각 컴포넌트를 건드리지 않는다.
- 외부 API 변경이나 대규모 아키텍처 리팩토링은 보류한다.

## 기대 결과
- `core/evolutionary_memory.py`/`utils/memory.py`의 주요 pathways를 테스트로 감싸 80% 이상 커버리지를 유지하고 안정성을 높인다.
- 문서(작업 로그, 릴리즈 노트, next_session)가 자동 반복 사이클 결과를 실시간으로 반영한다.

## 완료 기준
- `coverage run -m pytest` 및 `coverage report`에서 80% 이상 결과를 확보하고 테스트가 모두 통과.
- `docs/sessions/session_0056.md`에 해당 세션 로그를 기록하여 자동화 흐름을 남긴다.
