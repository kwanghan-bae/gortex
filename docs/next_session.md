# Next Session

## 세션 목표
- TUI 위젯 고도화 및 데이터 시각화 강화 (TUI Perfection Phase 2)

## 컨텍스트
- 리팩토링 유실 복구 및 테스트 커버리지 대폭 강화(60% 달성)로 시스템 안정화 완료.
- Web UI 중단 결정에 따라, 기술 부채 및 토론 현황 등 기존 웹 전용 데이터를 TUI에서 효과적으로 보여줘야 함.

## 범위 (Scope)
### 수행할 작업 (Do)
- `DashboardUI` 개선: `debt_list`, `active_debate` 데이터를 보여주는 전용 패널(Panel) 추가.
- `TerminalHandler`: 사용자 입력 처리 및 비동기 이벤트 루프 통합 최적화.
- `AnalystAgent`의 코드 리뷰 결과를 TUI에 실시간 반영하는 파이프라인 구축.
- `DashboardUI`의 레이아웃을 터미널 크기에 맞춰 동적으로 조정하는 기능 구현.

### 수행하지 않을 작업 (Do NOT)
- Web UI(React/Three.js) 관련 코드 수정 금지.
- 안정화된 코어 로직(`core/graph.py` 등)의 불필요한 변경 지양.

## 기대 결과
- 터미널만으로도 Gortex의 모든 고급 기능(토론, 리뷰, 부채 분석)을 모니터링하고 제어할 수 있는 완성형 TUI.

## 완료 기준
- 신규 TUI 위젯이 에러 없이 렌더링되고, 데이터 변경 시 실시간으로 업데이트됨.
