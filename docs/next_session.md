# Next Session

## 세션 목표
- 79% 커버리지를 유지하며 `core/commands.py`와 `utils/vector_store.py`의 핵심 흐름(명령 파싱·옵션, 벡터 업서트·검색)을 테스트로 감싼다.

## 컨텍스트
- `tests/test_notifier.py`/`tests/test_graph.py`로 커버리지를 79%까지 끌어올렸습니다.
- 자동 반복 사이클(`coverage run -m pytest` → `coverage report`)은 계속되고, 문서(릴리즈 노트/세션 로그/next_session)는 결과를 순차적으로 기록합니다.

## 범위 (Scope)
### 수행할 작업 (Do)
- `core/commands.py`: 명령 흐름 제어, 인식 실패/예외, 상태 업데이트, 로깅, 전환 로직을 Mock 기반으로 검증합니다.
- `utils/vector_store.py`: 벡터 업서트, 검색, 중복 방지, 부정확 결과 처리 경로를 시뮬레이션하여 데이터 무결성을 확보합니다.
- `coverage run -m pytest` → `coverage report` 사이클을 반복하고 문서(릴리즈 노트/세션 로그/next_session)를 갱신합니다.

### 수행하지 않을 작업 (Do NOT)
- Web UI(React/Three.js) 또는 `ui/three_js_bridge.py` 등 시각 컴포넌트 수정을 하지 않습니다.
- 새로운 외부 종속성이나 대규모 아키텍처 변경은 다음 루프로 연기합니다.

## 기대 결과
- `core/commands.py`/`utils/vector_store.py`의 주요 경로를 단위 테스트로 커버하여 전체 79% 이상을 유지합니다.
- 문서(작업 로그, 릴리즈 노트, next_session)가 방금 수행한 자동 반복 사이클 결과를 그대로 반영합니다.

## 완료 기준
- `coverage run -m pytest` 및 `coverage report`에서 79% 이상 결과와 모든 테스트 통과를 확보합니다.
- `docs/sessions/session_0055.md`에 해당 세션 로그를 등록해 자동화 흐름을 기록합니다.
