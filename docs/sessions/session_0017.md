# Session 0017

## Goal
- 작업 맥락 인지형 UI 레이아웃 및 테마 자동 전환 (Adaptive UI v1)

## What Was Done
- **agents/manager.py 수정**: `response_schema`에 `ui_mode` 필드 추가 및 작업 성격에 따라 최적의 모드(coding, research, debugging, analyst)를 선택하도록 지침 보강.
- **ui/dashboard.py 수정**: `ui_mode`에 따라 패널 비율(`ratio`)과 크기(`size`)를 동적으로 변경하는 `set_mode` 메서드 구현.
- **main.py 수정**: 에이전트 출력의 `ui_mode`를 감지하여 대시보드 레이아웃을 실시간으로 전환하도록 연동.

## Decisions
- 사용자의 몰입감을 위해 `coding` 모드에서는 사고 과정을, `research` 모드에서는 지식 베이스가 담긴 사이드바를 강조하도록 비율을 조정함.
- `debugging` 모드에서는 오류 분석이 용이하도록 로그 패널의 크기를 대폭 확대함.

## Problems / Blockers
- 현재 터미널 기반 UI의 한계로 인해 레이아웃 전환 시 일부 텍스트가 깜빡이거나 위치가 미세하게 어긋날 수 있음. 향후 렌더링 최적화 필요.

## Notes for Next Session
- 시스템의 '자율적 완성도'를 위해, 이제 작업이 완료된 후 사용자의 검토 없이도 스스로 최종 결과물을 아카이빙하고 관련 문서를 업데이트하는 'Auto-Finalizer' 기능이 필요함.
