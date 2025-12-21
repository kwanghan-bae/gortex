# Next Session

## Session Goal
- 작업 맥락 인지형 UI 레이아웃 및 테마 자동 전환 (Adaptive UI v1)

## Context
- 현재 대시보드 레이아웃은 고정되어 있어, 리서치 위주의 작업이나 대규모 리팩토링 시 중요한 정보가 가려질 수 있음.
- 에이전트가 현재 '리서치' 중이면 웹 검색 결과와 지식 노드를, '코딩' 중이면 시뮬레이션과 테스트 결과를 전면에 배치하는 동적 레이아웃 엔진이 필요함.

## Scope
### Do
- `agents/manager.py`에서 현재 작업의 성격(Context)을 분류하여 UI 상태로 전달.
- `ui/dashboard.py`에 작업 맥락에 따른 레이아웃 프리셋(Coding, Research, Debugging) 기능 추가.
- 매 턴마다 에이전트의 페르소나에 맞는 색상 테마 자동 적용.

### Do NOT
- 사용자가 설정한 기본 테마를 완전히 무시하지 말 것 (조화롭게 조절).

## Expected Outputs
- `agents/manager.py`, `ui/dashboard.py`, `main.py` 수정.

## Completion Criteria
- Researcher가 활동할 때는 리서치 패널이 강조되고, Coder가 활동할 때는 시뮬레이션 패널이 강조되는 동적 전환 과정이 확인되어야 함.
