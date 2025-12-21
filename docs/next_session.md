# Next Session

## Session Goal
- 에이전트 사고 트리 시각화 고도화 (Multimodal Thought UI v1)

## Context
- 현재 웹 대시보드에서 사고 트리(`thought_tree`)는 텍스트 위주로 노출됨.
- 에이전트가 복잡한 아키텍처를 설계할 때 Mermaid 코드를 사고 노드에 포함시키면, 웹 UI가 이를 실시간 다이어그램으로 렌더링하여 '시각적 추론'을 지원해야 함.

## Scope
### Do
- `agents/planner.py` 및 `agents/coder.py`의 `thought_tree` 스키마에 `visual_payload` 필드 추가.
- 에이전트가 중요 노드에 다이어그램 코드를 삽입하도록 지침 보강.
- 웹 UI(프론트엔드 가정)에서 해당 페이로드를 감지하여 다이어그램 팝업 또는 임베디드 뷰 제공.

### Do NOT
- 모든 노드에 강제로 시각 자료를 넣지 말 것 (복잡도가 높은 노드만 선별).

## Expected Outputs
- `docs/prompts/core_agents.yaml`, `agents/planner.py`, `ui/three_js_bridge.py` 수정.

## Completion Criteria
- 에이전트가 계획 수립 시 "설계 구조" 노드에 다이어그램 데이터를 포함하고, 이것이 대시보드 데이터 패킷에 정상적으로 포함되어 전송되는 것이 확인되어야 함.
