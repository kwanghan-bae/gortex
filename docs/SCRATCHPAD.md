# System 2 Scratchpad: Debate Memory Integration

## 1. Design Draft
- **EvolutionaryMemory Extension**:
    - `save_rule` 메서드에 `is_super_rule` 파라미터 추가.
    - Rule 딕셔너리에 `is_super_rule` 필드 추가 (Default: False).
    - `calculate_rule_value`에서 Super Rule은 `is_certified`와 마찬가지로 삭제되지 않도록 보호 (Value 100.0).
    - `get_active_constraints`에서 Super Rule은 우선순위를 높게 설정 (Certified보다 높거나 같게).

- **Swarm Integration**:
    - Swarm 토론 결과(Consensus)가 나오면 `EvolutionaryMemory.save_rule`을 호출.
    - 이때 `is_super_rule=True`로 설정.
    - Trigger Pattern은 토론 주제와 관련된 키워드로 자동 추출.

## 2. Edge Cases
- **Conflict**: Super Rule이 기존 Hard Rule과 충돌할 경우?
    - Hard Rule(`RULES.md`)은 코드 레벨이 아니라 문서 레벨이므로, 여기서는 Memory 내의 충돌을 의미함.
    - `detect_global_conflicts`가 이미 존재하므로, 충돌 감지 시 Super Rule이 이기도록 로직 수정 필요할 수 있음.
- **Empty Consensus**: 합의안이 도출되지 않은 경우 저장하지 않음.
- **Duplication**: 동일한 주제로 여러 번 토론 시 중복 저장 방지 (기존 `save_rule`의 중복 체크 로직 활용).

## 3. Implementation Plan
1. Modify `core/evolutionary_memory.py` to support `is_super_rule`.
2. Update `agents/swarm.py` (or wherever debate happens) to save consensus.
3. Add tests in `tests/test_evolutionary_memory.py`.
