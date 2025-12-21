# Next Session

## 세션 목표
- 70% 커버리지를 유지하면서 `ui/dashboard.py`, `utils/asset_manager.py`, `utils/table_detector.py`의 주요 흐름을 테스트로 확보한다.

## 컨텍스트
- 최근 메시지 큐, 로그 벡터화, Three.js 브리지를 포함한 테스트 확장으로 전체 커버리지가 70%를 기록했고 릴리즈 노트에 주요 건들을 정리했습니다.
- 자동 반복 사이클(`coverage run -m pytest` → `coverage report`)이 계속되며, 문서(릴리즈 노트/세션 로그/next_session)로 각 세션의 작업 상태를 추적하고 있습니다.

## 범위 (Scope)
### 수행할 작업 (Do)
- `ui/dashboard.py`의 레이아웃, 사이드바, 젠 애니메이션을 MagicMock한 Rich 객체로 렌더링하여 다양한 업데이트 흐름을 검증한다.
- `utils/asset_manager.py`의 아이콘/리소스 로딩, 캐싱, 실패 시 폴백 경로를 Mock 파일 기반으로 테스트한다.
- `utils/table_detector.py`의 텍스트/Markdown/CSV 입력을 조합해 테이블 판별과 행/열 추출이 일관되게 작동하는지 검증한다.
- `coverage run -m pytest` → `coverage report` 사이클을 반복해 통계를 기록하고 `docs/release_note.md`, `docs/sessions/session_XXXX.md`를 갱신한다.

### 수행하지 않을 작업 (Do NOT)
- Web UI(React/Three.js) 본체나 `ui/three_js_bridge.py` 내 그래픽 컴포넌트를 직접 변경하지 않는다.
- 대규모 아키텍처 리팩토링이나 새로운 에이전트 프로토콜 설계는 후속 세션으로 유보한다.

## 기대 결과
- 새 테스트들은 `ui/dashboard.py`, `utils/asset_manager.py`, `utils/table_detector.py`의 핵심 분기를 커버하여 70% 이상을 유지하고, 리포트에 개선 추세를 보여준다.
- 문서(작업 로그/릴리즈 노트/next_session)가 자동 반복 작업에 맞춰 최신 상태로 유지된다.

## 완료 기준
- `coverage run -m pytest` 및 `coverage report`로 70% 이상을 다시 기록하고, 테스트가 모두 통과.
- `docs/sessions/session_XXXX.md`에 해당 작업 세션 로그를 남겨 자동화 흐름을 문서화.
