# Next Session

## Session Goal
- 사용자 의도 투영 및 목표 그래프 시각화 (User Intent Projection v1)

## Context
- 현재 에이전트는 사용자의 단발성 명령을 처리하고 있으나, 사용자가 머릿속에 그리는 장기적인 '큰 그림'은 알지 못함.
- 사용자의 자연어 입력으로부터 '최종 목표'와 이를 이루기 위한 '세부 의도'들을 추출하여 웹 대시보드에 목표 그래프(Goal Graph)로 띄우고, 작업 진행에 따라 노드가 완성되는 시각적 동기화가 필요함.

## Scope
### Do
- `agents/manager.py`에서 사용자의 입력을 분석하여 '장기 목표'와 '단기 의도'를 구조화된 JSON으로 추출하는 로직 추가.
- `ui/three_js_bridge.py`에 목표 그래프(Goal Nodes) 생성 및 상태(Pending/In-Progress/Done) 업데이트 로직 추가.
- 사용자가 "내가 원하는 건 결국 X야"라고 말하면, 전체 목표 그래프가 즉시 재구성되는 인터랙티브 정렬 구현.

### Do NOT
- 기존의 인과 관계 그래프와 섞지 말 것 (사용자의 '의도'와 시스템의 '수행'은 별개 층위로 표현).

## Expected Outputs
- `agents/manager.py`, `ui/three_js_bridge.py`, `main.py` 수정.

## Completion Criteria
- 사용자 입력 시, 웹 대시보드 상단에 사용자의 의도를 구조화한 '의도 맵'이 나타나고, 에이전트의 활동이 해당 의도 노드에 수렴되는 과정이 확인되어야 함.
