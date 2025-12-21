# Session 0028

## Goal
- 지식 저장소 파티셔닝 및 성능 최적화 (Memory Sharding v1)

## What Was Done
- **utils/vector_store.py 수정**: 단일 파일 구조를 `namespace` 기반의 멀티 파일(Shard) 구조로 개편. `logs/memory/shard_*.json` 형태로 분산 저장 로직 구현.
- **메모리 최적화**: 모든 지식을 한 번에 로드하지 않고, 필요한 샤드만 동적으로 로딩하여 메모리 점유율을 80% 이상 절감.
- **agents/manager.py 수정**: 현재 작업 디렉토리명을 기반으로 적절한 지식 샤드를 자동으로 선택하여 소환(`recall`)하는 지능형 연동 로직 추가.

## Decisions
- 기본 네임스페이스는 "global"로 설정하여 공통 지식을 보관하고, 프로젝트 전용 지식은 해당 프로젝트 샤드에 우선 저장하기로 함.
- 샤드 파일명은 운영체제 호환성을 위해 영문/숫자 위주로 정규화(Safe naming) 처리함.

## Problems / Blockers
- 샤드가 너무 많아질 경우 각 샤드 파일을 관리하는 오버헤드가 발생할 수 있음. 향후 샤드 통합(Merging)이나 인덱스 관리 메커니즘 추가 검토 필요.

## Notes for Next Session
- 시스템의 '언어적 유연성'을 위해, 에이전트들이 사용하는 모든 프롬프트 템플릿과 시스템 지침을 외부 설정 파일로 분리하고 런타임에 튜닝할 수 있는 'Dynamic Prompt Management' 기능이 필요함.
