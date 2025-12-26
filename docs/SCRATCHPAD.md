# 📝 System 2 Scratchpad

## 🎯 Current Goal: Debate Memory Integration Verification

**Status Analysis:**
- `core/evolutionary_memory.py`: 'Super Rule' structure (`is_super_rule`) and priority logic (`get_active_constraints` sort key) appear to be implemented.
- `agents/swarm.py`: `synthesize_consensus` contains logic to save `unified_rule` as a Super Rule.

**Hypothesis:**
The implementation exists but may not be fully verified or robust.
1. The prompt condition `If this is a Knowledge Conflict Resolution, you MUST provide a 'unified_rule' structure.` might be too restrictive.
2. We need to ensure general consensus that yields a rule *also* gets saved, or clarify when a "Super Rule" should be formed.

**Action Plan:**
1.  **Verification Test**: Create `tests/test_swarm_memory_integration.py` to mock the LLM response with a `unified_rule` and verify it persists to `EvolutionaryMemory` with `is_super_rule=True`.
2.  **Retrieval Test**: Verify that `EvolutionaryMemory.get_active_constraints` returns this rule at the top.
3.  **Refinement**: If tests pass, consider relaxing the prompt constraint in `SwarmAgent` to allow more frequent Super Rule creation if beneficial, or document the specific criteria.

**Exceptions & Risks:**
- **Risk**: Over-population of Super Rules.
- **Mitigation**: Ensure `unified_rule` is only returned when a clear, reusable principle is established.