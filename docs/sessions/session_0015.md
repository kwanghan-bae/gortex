# Session 0015

## Goal
- 파일 수정 영향 범위 분석 및 시각화 (Dependency Impact Analyzer v1)

## What Was Done
- **utils/indexer.py 수정**: 특정 파일 수정 시 영향을 받는 직접/간접 모듈을 역추적하는 `get_impact_radius` 메서드 구현. AST 분석 데이터를 활용하여 Import 관계와 함수 호출 관계를 모두 고려함.
- **agents/planner.py 수정**: 계획 수립 시 '영향 범위 분석' 단계를 필수화하고, `impact_analysis` 결과를 시스템 메시지로 사용자에게 보고하도록 개선.
- **연속성 확보**: 이제 리팩토링이나 코드 수정 시, 해당 변경이 시스템 전체에 미치는 잠재적 리스크를 사전에 파악할 수 있음.

## Decisions
- 영향 범위 분석은 1단계(직접 참조)와 2단계(간접 참조)로 구분하여 보고함으로써 리스크의 강도를 차등화함.
- `Planner`의 응답 스키마를 확장하여 영향 분석 데이터를 구조화하고, 이를 `main.py`에서 실시간 메시지로 변환하도록 함.

## Problems / Blockers
- 현재 함수 호출 매칭이 단순 이름 기반이라, 서로 다른 모듈에서 동일한 이름을 가진 함수가 있을 경우 오탐(False Positive) 가능성이 있음. 향후 정규화된 심볼 ID 기반 매칭으로 고도화 필요.

## Notes for Next Session
- 시스템의 '운영 지능'을 강화하기 위해, 대규모 데이터 처리나 긴 대화 시 발생하는 메모리 병목을 감지하고 자동으로 최적화하는 'Dynamic Memory Pruning' 기능이 필요함.
