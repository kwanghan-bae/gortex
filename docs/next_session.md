# Next Session

## 세션 목표
- 전체 커버리지를 70% 이상으로 끌어올리기 위해 `core/commands.py`의 미검증 경로와 `ui/dashboard.py`, `utils/indexer.py`의 단순 기능들을 차례대로 테스트한다.

## 컨텍스트
- 최근 `utils/tools.py`와 `tests/test_commands.py` 개선으로 CLI 구동 경로가 일부 커버되었으나 전체 커버리지는 66%에 머무르고 있다.
- `coverage run -m pytest` → `coverage report` 결과를 기반으로, 핵심 TUI/에이전트/유틸 모듈의 취약 지점을 자동으로 점검하고 반복적으로 테스트를 추가해야 한다.

## 범위 (Scope)
### 수행할 작업 (Do)
- `/kg`, `/language`, `/export`, `/clear`, `/mode`, `/save`, `/load` 같은 `core/commands.py`의 여전히 미검증된 명령어 루트를 각기 새 테스트로 확인하여 제어 흐름을 확장한다.
- `ui/dashboard.py`의 레이아웃 생성기를 isolating하여 오프라인에서도 안정적으로 동작하도록 단위 테스트로 감싼다 (Rich 객체를 MagicMock로 대체).
- `utils/indexer.py`의 `scan_project`, `generate_map`, `search` API를 함수 수준에서 Mock을 활용해 시나리오별로 검증하고, 인덱싱 결과의 메타 데이터를 asserts로 확보한다.
- 자동화된 `coverage run -m pytest` → `coverage report` 사이클을 반복하여 변화치를 기록하고 `docs/release_note.md`/`docs/sessions/session_XXXX.md`에 반영한다.

### 수행하지 않을 작업 (Do NOT)
- Web UI(React/Three.js) 관련 코드 수정이나 대규모 아키텍처 리팩토링.
- 세션 텍스트를 무시하고 별도 기억을 두는 향상.

## 기대 결과
- 새롭게 작성한 테스트들이 커버리지 상의 공백을 메우고, 리포트 상 주요 모듈이 점진적으로 70%를 향해 이동한다.
- 자동 반복 작업이 종합 문서(next_session, release_note, session log)를 통해 이어지고 있다는 점이 분명히 드러난다.

## 완료 기준
- `coverage run -m pytest` 및 `coverage report`를 돌려 70% 목표를 넘긴 상태로 리포트를 저장.
- 새 테스트는 모두 통과하며, 관련 문서에 누적 작업 로그가 기록됨.
