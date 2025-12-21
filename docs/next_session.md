# Next Session

## 세션 목표
- 70% 커버리지 목표 달성을 위해 `utils/tools.py`, `utils/message_queue.py`, `utils/log_vectorizer.py`, `ui/three_js_bridge.py`의 핵심 흐름을 테스트로 발굴한다.

## 컨텍스트
- 최근 CLI, 인덱서, TUI 테스트를 확장하여 전체 커버리지는 68%까지 올라왔지만 `ui/`, `utils/` 일부 모듈이 여전히 낮은 상태다.
- 자동화된 `coverage run -m pytest` → `coverage report` 반복 과정을 통해 취약 모듈을 추적하며, 문서(릴리즈 노트, 세션 로그, next_session)도 실시간으로 갱신하고 있다.

## 범위 (Scope)
### 수행할 작업 (Do)
- `utils/tools.py`의 `execute_shell`, `archive_project_artifacts`, `compress_directory` 등 핵심 유틸리티의 동작/경계 조건을 위한 단위 테스트를 추가한다.
- `utils/message_queue.py`, `utils/log_vectorizer.py`의 상태 변화 및 이벤트 처리 시나리오를 Mock 환경에서 검증하여 커버리지를 확장한다.
- `ui/three_js_bridge.py`의 `convert_thought_to_3d` 등 3D 관련 보조 기능을 최소 복제 피처로 감싼 테스트를 작성하고, `DashboardUI`와의 연동 흐름을 일부 확인한다.
- `coverage run -m pytest` → `coverage report` 사이클에서 통계를 수집하고, `docs/release_note.md`, `docs/sessions/session_XXXX.md`에 현황을 기록한다.

### 수행하지 않을 작업 (Do NOT)
- Web UI(React/Three.js) 관련 코드 수정이나 대규모 아키텍처 리팩토링.
- 독립적인 세션 메모리를 외부에 보관하거나 문서 기록 없이 진행하는 작업.

## 기대 결과
- 새 테스트들이 `utils/`, `ui/three_js_bridge`를 중심으로 70% 커버리지 방향을 뚜렷하게 높이며, 리포트 상 주요 모듈의 최소 수치를 개선한다.
- 문서(작업 로그/릴리즈 노트/next_session)가 자동화 흐름에 따라 최신 상태로 유지되는 패턴이 명확히 드러난다.

## 완료 기준
- `coverage run -m pytest` 및 `coverage report`를 실행해 70% 목표를 향한 추세를 기록.
- 작성한 테스트가 모두 통과하고 `docs/sessions/session_XXXX.md`에 작업 로그를 남김.
