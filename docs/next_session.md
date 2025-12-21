# Next Session

## 세션 목표
- 75% 커버리지를 유지하며 `core/auth.py`와 `core/observer.py`의 흐름 및 에러 핸들링을 단위/통합 테스트로 검증한다.

## 컨텍스트
- `tests/test_translator.py`와 `tests/test_engine.py`의 추가로 번역기와 엔진 루프가 단단해졌으며, 전체 커버리지는 75%로 상승했습니다.
- 자동 반복 사이클(`coverage run -m pytest` → `coverage report`)은 계속되며, 릴리즈 노트·세션 로그·next_session으로 매 세션 결과를 기록하고 있습니다.

## 범위 (Scope)
### 수행할 작업 (Do)
- `core/auth.py`의 인증 플로우(토큰 발급, 권한 확인, 인증 실패)를 Mock된 요청/응답으로 검증해 보안 케이스를 커버한다.
- `core/observer.py`의 이벤트 로깅, causal graph, 상태 변경을 지표화하여 `publish_event`/`log_event` 경로를 테스트로 확보한다.
- `coverage run -m pytest` → `coverage report` 사이클을 반복하고 레포트 결과를 `docs/release_note.md`, `docs/sessions/session_XXXX.md`에 반영한다.

### 수행하지 않을 작업 (Do NOT)
- Web UI(React/Three.js) 또는 `ui/` 자산을 직접 변경하지 않는다.
- 대규모 구조 리팩토링이나 외부 API 통합은 다음 사이클로 미룬다.

## 기대 결과
- 새 테스트들은 `core/auth.py`/`core/observer.py`의 인증, 이벤트 로깅, 예외 경로를 커버하여 75% 이상의 커버리지를 유지한다.
- 문서(작업 로그, 릴리즈 노트, next_session)가 자동 반복 작업에 맞춰 최신 상태로 유지된다.

## 완료 기준
- `coverage run -m pytest` 및 `coverage report`에서 75% 이상 결과를 기록하고, 관련 테스트가 모두 통과.
- `docs/sessions/session_XXXX.md`에 해당 세션 로그를 등록하여 자동화 흐름을 문서화.
