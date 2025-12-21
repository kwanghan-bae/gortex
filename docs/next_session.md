# Next Session

## Session Goal
- UI 시스템 모듈화 및 테스트 커버리지 대폭 확대 (Testing Blitz v1)

## Context
- v2.7.2에서 핵심 로직 모듈화가 성공적으로 안착됨.
- 이제 `ui/dashboard.py`와 `ui/three_js_bridge.py`의 비대한 로직을 컴포넌트별로 분리하고, 전체 시스템의 테스트 케이스를 100개 이상으로 확장해야 함.

## Scope
### Do
- `ui/dashboard.py`를 `LayoutManager`, `WidgetHandler`, `WebStreamer` 등으로 분리.
- `ui/three_js_bridge.py`를 좌표 변환기와 기하 데이터 생성기로 분리.
- 분리된 모든 모듈에 대해 경계값 및 예외 상황 테스트 50개 이상 신규 추가.

### Do NOT
- 시각적 디자인이나 기능을 변경하지 말 것 (오직 구조적 개선 및 검증 강화).

## Expected Outputs
- `ui/` 하위 신규 모듈들, `tests/` 내 대량의 신규 테스트 파일.

## Completion Criteria
- 모든 거대 파일의 300라인 이하 달성 및 `pre_commit.sh` 커버리지 확인 시 테스트 케이스 100개 이상 통과.
