# Session 0027

## Goal
- 사용자 의도 투영 및 목표 그래프 시각화 (User Intent Projection v1)

## What Was Done
- **agents/manager.py 수정**: 사용자의 자연어 입력에서 장기 목표(`big_picture`)와 단계별 의도(`intent_nodes`)를 추출하는 로직 및 응답 스키마 추가.
- **ui/three_js_bridge.py 수정**: 의도 데이터를 상단 목표 레이어의 3D 노드와 엣지로 변환하는 `convert_intent_to_3d` 메서드 구현. 상태별(Done, In-Progress, Pending) 색상 매핑 적용.
- **main.py 연동**: 매 턴 에이전트의 의도 분석 결과를 웹 대시보드로 실시간 스트리밍하여 시각적 로드맵을 제공하도록 통합.
- **Bug Fix**: `main.py` 내의 잘못된 텍스트 주입으로 인한 구문 오류 해결.

## Decisions
- 사용자의 의도(Goal)와 시스템의 수행(Trace)을 별개의 3D 레이어(상/하)로 분리하여 표현함으로써, 추상적 목표가 구체적 행동으로 수렴되는 과정을 가시화함.
- 의도 노드는 인과 그래프보다 높은 위치(Y=100)에 배치하여 '북극성'과 같은 가이드 역할을 하게 함.

## Problems / Blockers
- 사용자의 발언이 매우 짧거나 모호할 경우 의도 추출의 정확도가 떨어질 수 있음. 향후 이전 대화 맥락을 더 길게 참조하여 의도를 보정하는 로직 필요.

## Notes for Next Session
- 시스템의 '기억 구조'를 물리적으로 고도화하기 위해, 현재 단일 파일로 관리되는 `LongTermMemory`를 프로젝트 규모에 맞게 파티셔닝하고 검색 성능을 최적화하는 'Memory Sharding & Indexing'이 필요함.
