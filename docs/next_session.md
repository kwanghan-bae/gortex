# Next Session

## Session Goal
- **Visual Reputation & Skill Tree**: 에이전트별 평판뿐만 아니라, 코딩(`Coding`), 조사(`Research`), 설계(`Design`), 분석(`Analysis`) 등 각 분야에서의 전문성 점수를 TUI 대시보드에 스킬 트리(Skill Tree) 형태로 시각화한다.

## Context
- `Session 0089`에서 평판 리더보드를 구축했으나, 총점만 보여주므로 에이전트의 강점 파악이 어려움.
- 에이전트가 특정 분야의 작업을 성공할 때마다 해당 분야의 스킬 포인트를 별도로 적립함.
- 시각적으로 '성장하는 직원'의 느낌을 주어 사용자 경험을 강화함.

## Scope
### Do
- `utils/economy.py`: 분야별 스킬 포인트(`skill_points`) 추적 필드 추가.
- `ui/dashboard.py`: 평판 패널(`economy`) 하위에 분야별 숙련도를 막대 그래프로 보여주는 렌더링 로직 추가.
- `agents/analyst/reflection.py`: 작업 품질 평가 시 분야(Category)를 판별하여 스킬 포인트 가중치 도출.

### Do NOT
- 실제 게임 같은 복잡한 스킬 해금(Unlock) 로직은 다음 단계로 미룸.

## Expected Outputs
- `utils/economy.py` (Update)
- `ui/dashboard.py` (Update)
- `tests/test_skill_tree.py` (New)

## Completion Criteria
- Coder가 코딩 작업을 성공했을 때, 평판 포인트와 함께 `Coding` 스킬 포인트가 동시에 오르고 대시보드에 반영되어야 함.
- `docs/sessions/session_0093.md` 기록.
