# Next Session

## 세션 목표
- 미뤄뒀던 TUI 안정화 작업을 재개하여 `ui/terminal.py` 및 `ui/dashboard.py`의 테스트 커버리지를 80% 이상으로 끌어올린다.

## 컨텍스트
- `core/llm` 추상화 및 `utils/memory.py` 적용을 통해 로컬 모델 도입 기반(Phase 1)을 성공적으로 마쳤습니다.
- Phase 2(Coder 적용)는 설계가 완료되었으나 실제 구현은 복잡도가 높으므로, 잠시 숨을 고르며 시스템의 얼굴인 TUI의 안정성을 확보하는 것이 전략적으로 유리합니다.

## 범위 (Scope)
### 수행할 작업 (Do)
- `tests/test_ui.py`: 기존 UI 테스트를 확장하여 `ui/terminal.py`의 Rich 라이브러리 렌더링 로직을 Mocking 검증.
- `ui/dashboard.py`: 대시보드 갱신 루프 및 이벤트 핸들링 로직의 예외 처리를 테스트.
- `coverage run`: UI 모듈 커버리지 측정 및 목표(80%) 달성 확인.

### 수행하지 않을 작업 (Do NOT)
- `Coder`의 로컬 모델 적용 구현은 이번 세션에서 진행하지 않는다.

## 기대 결과
- 사용자가 직접 마주하는 터미널 인터페이스의 버그를 사전에 차단하고 신뢰성을 높인다.

## 완료 기준
- `ui/terminal.py` 커버리지 80% 이상.
- `ui/dashboard.py` 커버리지 80% 이상.
- `docs/sessions/session_0061.md` 기록.