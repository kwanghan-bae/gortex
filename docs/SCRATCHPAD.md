# 📝 System 2 Scratchpad

## 🎯 Current Goal: Local Execution Optimization & Architecture Decoupling

**Context Analysis:**
- Current implementation relies heavily on Redis and MQ for `vector_store` and agent communication, which is overkill for a local, single-user environment.
- The user wants a lightweight, standalone local mode ("Local First") while keeping the door open for multi-cloud expansion ("Distributed Mode").
- Usability should match `gemini-cli` or `claude-cod`.

**Hypothesis & Strategy:**
1.  **Dependency Inversion**:
    - Abstract `MemoryStorage` and `MessageBroker` interfaces.
    - Implement `LocalMemory` (SQLite/JSON) vs `RedisMemory`.
    - Implement `LocalBroker` (In-Memory Queue) vs `RedisBroker`.
2.  **Configuration**:
    - Introduce `GORTEX_ENV` (local | distributed) to switch implementations at runtime.
3.  **TDD approach**:
    - Write tests for the `Local` implementations first.
    - Ensure the TUI works without any external services running (no `docker compose` needed for basic usage).

**Plan of Action:**
1.  **Audit**: Scan codebase for `redis`, `amqp`, etc. to find hard dependencies.
2.  **Abstract**: Create base classes/interfaces for these services.
3.  **Implement Local**: Build the lightweight versions.
4.  **Integration**: Wire up `settings.py` to choose the implementation.
5.  **Verify**: Run the full agent loop in "Local Mode" via TUI.

**Anti-Entropy (Risks):**
- **Complexity**: Over-engineering the abstraction might make the code harder to read. -> Keep it simple: Strategy Pattern.
- **Breaking Changes**: Existing distributed features might break. -> Run existing tests with `GORTEX_ENV=distributed` (mocked) if possible, but prioritize local stability now.