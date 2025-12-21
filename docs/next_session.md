# Next Session

## Session Goal
- 지식 계보 시각화 및 추론 근거 노출 (Knowledge Lineage UI v1)

## Context
- 시스템에 다양한 출처의 지식이 쌓이고 있으나, 에이전트가 답변할 때 실제로 어떤 지식을 참고했는지 사용자가 알기 어려움.
- `LongTermMemory.recall` 결과를 대시보드 UI에 별도 패널로 노출하고, 인과 관계 그래프 노드와 연결하여 '지식의 계보'를 시각화해야 함.

## Scope
### Do
- `ui/dashboard.py`에 현재 참조 중인 지식 목록을 보여주는 `Knowledge Source` 패널 추가.
- `agents/manager.py`에서 `Recall`된 지식의 출처(Metadata)를 UI 상태로 전달하도록 수정.
- 웹 대시보드 3D 그래프에서 지식 노드와 에이전트 노드 간의 동적 연결선(Edges) 강화.

### Do NOT
- 단순히 텍스트만 나열하지 말고, 출처별(LiveDocs, 패턴 등) 아이콘과 강조색을 활용할 것.

## Expected Outputs
- `ui/dashboard.py`, `agents/manager.py`, `main.py` 수정.

## Completion Criteria
- 에이전트 답변 시, 사이드바나 메인 패널에 "참고된 지식: [출처] 내용"이 시각적으로 표시되는 것이 확인되어야 함.