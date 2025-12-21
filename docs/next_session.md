# Next Session

## 세션 목표
- 75% 커버리지를 유지하며 `utils/tools.py`와 `utils/message_queue.py`의 핵심 경계 조건 및 fallback 시나리오를 테스트로 확보한다.

## 컨텍스트
- 인증/로깅/엔진/번역 테스트를 통해 75% 커버리지를 달성했고, 현재 주기는 `core/auth.py`와 `core/observer.py`를 집중 검증하며 문서화를 마무리했습니다.
- 자동 반복 사이클(`coverage run -m pytest` → `coverage report`)은 계속되며, 문서(릴리즈 노트/세션 로그/next_session)로 각 세션의 작업 흐름을 기록하고 있습니다.

## 범위 (Scope)
### 수행할 작업 (Do)
- `utils/tools.py`의 `list_files`, `execute_shell`, `archive_project_artifacts`, `compress_directory` 등에 대한 더 정교한 파일/압축 경로, timeout, 실패 복구 시나리오를 테스트로 추가한다.
- `utils/message_queue.py`에서 Redis 없음, publish/push/pop, 에러 처리 흐름을 Mock 기반으로 검증하여 큐 신뢰성을 높인다.
- `coverage run -m pytest` → `coverage report` 사이클을 반복하며 통계를 기록하고 `docs/release_note.md`, `docs/sessions/session_XXXX.md`를 갱신한다.

### 수행하지 않을 작업 (Do NOT)
- Web UI(React/Three.js) 또는 `ui/three_js_bridge.py` 그래픽 컴포넌트를 직접 변경하지 않는다.
- 대규모 아키텍처 리팩토링이나 새로운 외부 API 통합은 다음 사이클로 미룬다.

## 기대 결과
- `utils/tools.py`와 `utils/message_queue.py`의 경계/에러 대응 흐름을 테스트로 포섭하여 75% 이상 커버리지를 유지하고 안정성을 강화한다.
- 문서(작업 로그, 릴리즈 노트, next_session)가 자동 반복 작업에 맞춰 최신 상태로 유지된다.

## 완료 기준
- `coverage run -m pytest` 및 `coverage report`로 75% 이상 결과를 확보하고, 관련 테스트가 모두 통과.
- `docs/sessions/session_XXXX.md`에 해당 세션 로그를 남겨 자동화 흐름을 기록.
