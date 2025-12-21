# Next Session

## 세션 목표
- TUI 우선 순위 전략에 따라 `ui/dashboard.py`, `ui/dashboard_theme.py`, `ui/terminal.py`의 테스트 커버리지를 80% 이상으로 확보한다.

## 컨텍스트
- `core/evolutionary_memory.py`와 `utils/memory.py`는 100% 커버리지를 달성하여 기억 계층의 안정성을 확보했습니다.
- 현재 TUI(Terminal UI) 집중 전략에 따라 사용자와의 인터페이스인 Dashboard 및 Terminal 모듈의 신뢰성을 높여야 합니다.

## 범위 (Scope)
### 수행할 작업 (Do)
- `ui/terminal.py`: 터미널 입력, 출력 렌더링 및 Rich 라이브러리 연동 로직을 Mock 기반으로 검증한다.
- `ui/dashboard_theme.py`: 테마 설정, 색상 팔레트 및 레이아웃 구성 상수를 검증한다.
- `ui/dashboard.py`: 대시보드 업데이트, 노드 상태 시각화 및 이벤트 루프 안정성을 테스트한다.
- `coverage run -m pytest` → `coverage report` 사이클을 반복하여 80% 이상의 커버리지를 달성한다.

### 수행하지 않을 작업 (Do NOT)
- Web UI 관련 `ui/web_server.py` 및 `ui/three_js_bridge.py`의 복잡한 시각화 로직은 우선순위에서 제외한다.
- 코어 엔진(`core/engine.py`)의 대규모 리팩토링은 수행하지 않는다.

## 기대 결과
- TUI 핵심 모듈들의 커버리지가 80% 이상으로 상승하여 사용자 인터페이스의 안정성이 강화된다.
- 문서(작업 로그, 릴리즈 노트, next_session)가 최신화된다.

## 완료 기준
- `ui/dashboard.py`, `ui/dashboard_theme.py`, `ui/terminal.py`의 커버리지가 각각 80% 이상 달성.
- 모든 단위 테스트 통과.
- `docs/sessions/session_0058.md` 기록 완료.