# Next Session

## 세션 목표
- 핵심 유틸 및 에이전트 테스트를 보완하여 전체 커버리지 70% 이상을 확보한다.

## 컨텍스트
- 최근 `utils/tools.py`의 `list_files`/`read_file` 두 함수가 커버리지 어설션을 깨뜨렸으나 수정 완료.
- 사용자 요청대로 테스트 커버리지 향상에 집중하면서 TUI 고도화는 진행 중인 상태로, 잠시 대기 상태로 유지한다.

## 범위 (Scope)
### 수행할 작업 (Do)
- 커버리지가 낮은 `core/commands.py`, `ui/dashboard.py`, `agents/manager.py` 등 핵심 모듈을 조사하여 누락된 테스트 케이스를 정의.
- `tests/`에 새로운 `pytest` 기반 테스트를 추가하여 로직 순환, TUI 데이터 흐름, 에러 경로를 검증.
- `coverage run -m pytest` 결과를 기록하여 `core/`, `agents/`, `utils/`에서 70% 이상 커버리지가 달성되었음을 증명.

### 수행하지 않을 작업 (Do NOT)
- Web UI(React/Three.js) 및 `core/graph.py` 등 안정화된 그래프 컴파일 로직을 수정하지 않는다.
- 대규모 아키텍처 리팩토링이나 새로운 에이전트 프로토콜 설계는 다음 세션 이후로 유보.

## 기대 결과
- 추가된 테스트들이 해당 모듈의 핵심 분기와 실패 조건을 검증하여 커버리지 리포트가 70% 이상으로 상승함.
- `utils/tools.py` 로그/트래킹도 안정되어 반복 실행 시에도 커버리지 수치가 깨지지 않음.

## 완료 기준
- `PYTHONPATH=/Users/joel/Desktop/git coverage run -m pytest` 및 `coverage report` 실행 결과가 요구 범위를 만족.
- 새로 작성한 테스트가 모두 통과하고 `tests/` 하위에 커버리지 주석 또는 설명을 함께 남김.
