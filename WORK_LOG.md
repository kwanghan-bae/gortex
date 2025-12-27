# Work Log

## 2025-12-27: Local Mode Optimization (Joel)

### Goal
- Configure Gortex to run locally without heavy dependencies (Redis).
- Ensure "Local First" architecture while maintaining "Distributed" capability.

### Changes
1.  **Storage Abstraction**:
    -   Created `core/storage.py` defining `StorageProvider` interface.
    -   Implemented `SqliteStorage` (for local persistence in `.gortex/storage.db`) and `RedisStorage`.
2.  **Message Queue Refactoring (`core/mq.py`)**:
    -   Updated `GortexMessageBus` to use `StorageProvider`.
    -   Implemented in-memory Local PubSub mechanism for standalone execution.
    -   Configured `env` detection via `settings.GORTEX_ENV`.
3.  **Core Components Update**:
    -   `core/evolutionary_memory.py`: Switched to `mq.storage` (removes manual file fallback duplication).
    -   `core/persistence.py`: Switched to `mq.storage` for state mirroring.
    -   `utils/vector_store.py`: Switched to `mq.storage` and enabled sync listener in local mode.
4.  **System Integrity**:
    -   `core/system.py`: Removed `is_connected` check to allow local notifications (Thought Stream, Task Completion) to flow via Local PubSub.
    -   Fixed `SyntaxError` in `core/system.py`.
5.  **Tests**:
    -   Fixed `tests/test_evolutionary_memory.py` and `tests/test_vector_store.py` by properly patching `mq_bus` and `storage` to ensure test isolation.
    -   Verified all relevant tests pass.

### Result
- Gortex can now run in `local` mode (default) using SQLite and In-Memory MQ.
- TUI should function correctly without Redis.
