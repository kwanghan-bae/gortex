# Next Session

## Session Goal
- **Dynamic Context Pruning**: 대화가 길어질 때 핵심 컨텍스트는 유지하면서 불필요한 메시지를 지능적으로 삭제하거나 요약하여, 모델의 인지 효율을 극대화하고 토큰 비용을 절감한다.

## Context
- `Session 0085`에서 로컬 모델 폴백을 구축했으나, 로컬 모델은 클라우드 모델보다 컨텍스트 크기에 더 민감함.
- 현재 메시지가 무한정 쌓이는 구조는 성능 저하와 비용 증가를 초래함.
- `GortexState`의 `history_summary` 필드를 적극 활용하여 과거 대화를 압축할 필요가 있음.

## Scope
### Do
- `utils/memory.py`: 메시지 중요도 평가 및 가지치기(Pruning) 알고리즘 구현.
- `core/llm/summarizer.py` (New): 하위 호환성을 유지하며 대화 이력을 요약하는 전용 모듈 신설.
- `core/graph.py`: 매 노드 실행 후 컨텍스트 크기를 체크하고 필요시 요약을 트리거하는 로직 연동.

### Do NOT
- 사용자가 명시적으로 `pinned_messages`에 넣은 내용은 절대 삭제하지 않음.

## Expected Outputs
- `utils/memory.py` (Update)
- `core/llm/summarizer.py` (New)
- `tests/test_context_pruning.py` (New)

## Completion Criteria
- 메시지가 20개 이상 쌓였을 때, 자동으로 상위 10개를 요약본으로 변환하고 전체 메시지 수를 절반 이하로 줄여야 함.
- `docs/sessions/session_0086.md` 기록.