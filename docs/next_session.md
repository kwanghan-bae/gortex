# Next Session

## 세션 목표
- 70% 커버리지를 유지하면서 `utils/translator.py`와 `core/engine.py`의 핵심 흐름 및 에러 조건을 테스트로 검증한다.

## 컨텍스트
- `tests/test_ui.py`, `tests/test_asset_manager.py`, `tests/test_table_detector.py`의 추가로 UI/유틸 흐름이 강화되었고 커버리지 70%를 달성했습니다.
- 자동화 사이클(`coverage run -m pytest` → `coverage report`)은 계속되며, 문서(릴리즈 노트/세션 로그/next_session)는 즉각 반영하고 있습니다.

## 범위 (Scope)
### 수행할 작업 (Do)
- `utils/translator.py`의 `SynapticTranslator` 또는 i18n 포함 기능을 Mock된 파일/데이터로 검증하여 언어 전환, 기본값, 에러 처리 커버리지를 확보한다.
- `core/engine.py`의 주요 루프, 단계별 `handle_step`/`execute_step` 흐름을 테스트하여 plan/result 이벤트를 명시적으로 확인한다.
- `coverage run -m pytest` → `coverage report` 사이클을 반복하며 통계를 기록하고 `docs/release_note.md`, `docs/sessions/session_XXXX.md`를 갱신한다.

### 수행하지 않을 작업 (Do NOT)
- Web UI(React/Three.js)나 `ui/` 모듈에 새로운 그래픽 컴포넌트를 추가하지 않는다.
- 커다란 아키텍처 리팩토링이나 새로운 외부 통합은 다음 주기로 미룬다.

## 기대 결과
- 새 테스트들은 `utils/translator.py`, `core/engine.py`의 분기/에러 처리를 커버하여 70% 이상을 유지하며 안정성을 높인다.
- 문서(작업 로그/릴리즈 노트/next_session)가 자동 흐름에 맞춰 계속 최신 상태로 유지된다.

## 완료 기준
- `coverage run -m pytest` 및 `coverage report`에서 70% 이상의 결과를 확보하고 관련 테스트가 모두 통과.
- `docs/sessions/session_XXXX.md`에 이번 세션 로그를 남겨 자동화 흐름을 기록.
