# Next Session

## Session Goal
- **Decentralized Knowledge Search (Memory Sharding)**: 하나의 거대한 파일(`experience.json`)로 관리되던 지식 베이스를 분야별(Coding, Research 등) 또는 프로젝트별 독립적인 조각(Shard)으로 분산 저장하고, 현재 맥락에 필요한 조각만 선택적으로 로드하여 검색 속도와 인지 정확도를 높인다.

## Context
- 100회 이상의 세션을 거치며 `experience.json`에 수십 개의 규칙이 쌓였음.
- 모든 규칙을 매번 로드하여 프롬프트에 넣는 것은 토큰 낭비와 모델의 집중력 저하를 유발함.
- 지식의 '관심사 분리'를 통해 고밀도 지능을 유지함.

## Scope
### Do
- `core/evolutionary_memory.py`: 지식을 샤드(Shard) 단위로 저장하고 관리하는 `ShardedMemory` 클래스로 진화.
- `core/evolutionary_memory.py`: 현재 맥락(`context_text`)과 가장 관련성이 높은 샤드를 동적으로 탐색하는 `pick_shards` 로직 구현.
- `utils/tools.py`: 샤드 간의 중복 데이터를 동기화하거나 정리하는 유틸리티 보강.

### Do NOT
- 기존 `experience.json`과의 하위 호환성을 깨지 않음 (마이그레이션 도구 포함).

## Expected Outputs
- `core/evolutionary_memory.py` (Sharding support)
- `logs/memory/` (New directory for shards)
- `tests/test_memory_sharding.py` (New)

## Completion Criteria
- 코딩 작업 중에는 `coding_shard.json`의 지식이 우선적으로 주입되어야 함.
- 전체 지식 파일 크기가 줄어들지 않더라도, 매 요청 시 로드되는 토큰 양은 50% 이상 감소해야 함.
- `docs/sessions/session_0112.md` 기록.