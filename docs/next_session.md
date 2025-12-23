# Next Session

## Session Goal
- **Intelligent Context Pruning & Relevance Ranking**: 세션 내 메시지나 로그가 길어질 때, 단순히 전체를 요약하는 대신 현재 작업 목표(`state.plan`)와의 '관련성 점수(Relevance Score)'를 매겨, 중요도가 낮은 메시지를 선택적으로 제거(Pruning)하고 핵심 정보의 밀도를 극대화하는 지능형 압축 엔진을 구축한다.

## Context
- 현재 Gortex는 메시지가 일정 개수를 넘으면 `summarizer`를 통해 전체를 하나로 합침.
- 이 과정에서 과거의 구체적인 명령이나 도구 출력 결과 등 '디테일'이 유실되는 부작용이 있음.
- 현재 해결 중인 작업 단계와 관련이 깊은 메시지는 원본을 유지하고, 관련 없는 노이즈만 쳐내는 정밀한 컨텍스트 관리가 필요함.

## Scope
### Do
- `utils/memory.py`: 메시지별 관련성을 계산하고 가지치기를 수행하는 `ContextPruner` 클래스 추가.
- `core/engine.py`: 노드 실행 전 컨텍스트 가지치기 로직을 주입하여 에이전트에게 전달되는 토큰 최적화.
- `agents/analyst/base.py`: 메시지의 가치를 평가하는 LLM 기반의 `rank_context_relevance` 지침 추가.

### Do NOT
- `pinned_messages`(고정 메시지)는 어떠한 경우에도 가지치기 대상에서 제외함.

## Expected Outputs
- `utils/memory.py` (Context Pruner)
- `tests/test_context_pruning.py` (New)

## Completion Criteria
- 컨텍스트 길이가 임계치를 넘었을 때, 현재 단계와 관련 없는 과거 메시지 3개 이상이 정확히 제거되어야 함.
- 가지치기 후에도 에이전트가 현재의 핵심 작업 목표를 완벽히 인지하고 있어야 함.
- `docs/sessions/session_0123.md` 기록.
