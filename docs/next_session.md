# Next Session

## 세션 목표
- 78% 커버리지를 유지하면서 `utils/notifier.py`와 `core/graph.py`의 핵심 경로(메시지/알림 생성, 노드·간선 구성, 예외 복구)를 검증하는 테스트를 추가한다.

## 컨텍스트
- `tests/test_tools.py`/`tests/test_message_queue.py`를 통해 도구 유틸리티와 큐 흐름을 보강했고, 전체 커버리지는 78%로 상승했습니다.
- 자동 반복 사이클(`coverage run -m pytest` → `coverage report`)은 계속되며, 문서(릴리즈 노트/세션 로그/next_session)가 각 세션의 결과를 기록하고 있습니다.

## 범위 (Scope)
### 수행할 작업 (Do)
- `utils/notifier.py`의 알림 페이로드 생성, 제목/본문 조합, 실패/재시도 조건을 Mock된 설정과 `logging` 관찰로 검증한다.
- `core/graph.py`의 causal graph building, cycle handling, missing nodes/edges, 디스크 쓰기(flush) 관련 흐름을 테스트하여 안정적인 시각화 데이터를 확보한다.
- `coverage run -m pytest` → `coverage report` 사이클을 반복하며 통계를 기록하고 `docs/release_note.md`, `docs/sessions/session_XXXX.md`를 갱신한다.

### 수행하지 않을 작업 (Do NOT)
- Web UI(React/Three.js) 또는 `ui/three_js_bridge.py`의 시각 컴포넌트를 직접 변경하지 않는다.
- 대규모 아키텍처 리팩토링이나 새로운 외부 API 통합은 다음 주기로 미룬다.

## 기대 결과
- `utils/notifier.py`와 `core/graph.py`의 메시지/그래프 경로를 테스트로 감싸 78% 이상의 커버리지를 유지하고 신뢰성을 높인다.
- 문서(작업 로그, 릴리즈 노트, next_session)가 자동 반복 작업에 맞춰 최신 상태로 유지된다.

## 완료 기준
- `coverage run -m pytest` 및 `coverage report`에서 78% 이상 결과를 확보하고, 관련 테스트가 모두 통과.
- `docs/sessions/session_XXXX.md`에 해당 세션 로그를 남겨 자동화 흐름을 기록.
