# Next Session

## Session Goal
- 핵심 설계 의사결정 및 컨텍스트 자동 고정 (Context Pinning v1)

## Context
- `Memory Pruning`을 통해 메시지가 요약되고 삭제되면서, 이전 세션에서 합의된 미세한 설계 결정이나 임시 규칙이 유실될 위험이 있음.
- 사용자가 "이 결정은 중요해"라고 하거나 `Analyst`가 'Critical Decision'으로 분류한 내용은 `messages` 리스트의 삭제 대상에서 제외하고 항상 최상단에 배치(Pinning)해야 함.

## Scope
### Do
- `core/state.py`에 `pinned_messages` 필드 추가.
- `utils/memory.py`의 `prune_synapse` 로직을 수정하여 `pinned_messages`를 항상 보존하고 프롬프트 최상단에 주입하도록 개선.
- 에이전트 응답 스키마에 `pin_this` (boolean) 필드를 추가하여 자율적인 정보 중요도 판정 유도.

### Do NOT
- 모든 메시지를 고정하지 말 것 (토큰 낭비 방지를 위해 진짜 핵심만 선별).

## Expected Outputs
- `core/state.py`, `utils/memory.py`, `agents/manager.py` 수정.

## Completion Criteria
- 메시지 가지치기(Pruning)가 발생한 후에도, '고정된 메시지'들이 프롬프트 내에 온전히 남아있는 것이 확인되어야 함.
