# Next Session

## Session Goal
- **Distributed State Replication**: 여러 세션이나 다양한 환경에서도 동일한 `GortexState`를 유지하고 복구할 수 있도록, 상태 데이터를 주기적으로 외부 영속성 계층(Redis 또는 암호화된 Shared JSON)에 실시간 복제(Replication)하고 동기화하는 상태 엔진을 구축한다.

## Context
- 현재 상태는 메모리(`MemorySaver`)나 로컬 SQLite에 의존하고 있어, 프로세스 종료 시나 특정 환경에서 유실될 위험이 있음.
- 시스템의 '연속성'을 보장하기 위해, 상태를 원격으로 공유하거나 강력한 파일 기반 동기화를 지원해야 함.
- 이는 미래의 '다중 노드 Gortex'를 위한 필수 기초 작업임.

## Scope
### Do
- `core/persistence.py` (New): `DistributedSaver` 인터페이스 및 구현체 추가.
- `core/state.py`: 상태 복제 시점(Checkpointing)과 동기화 전략 정의.
- `main.py`: 새로운 영속성 계층을 워크플로우 그래프에 연동.

### Do NOT
- 실제 분산 서버 인프라 구축은 배제 (추상화된 클라이언트 로직 위주).

## Expected Outputs
- `core/persistence.py` (New Persistence Layer)
- `core/state.py` (Updated schema for sync metadata)
- `tests/test_state_replication.py` (New)

## Completion Criteria
- 시스템 종료 후 재시작 시, 로컬 저장이 아닌 '복제된 저장소'로부터 이전 상태를 100% 복원해야 함.
- 상태 변경 시 복제 지연(Latency)이 100ms 이내여야 함.
- `docs/sessions/session_0115.md` 기록.
