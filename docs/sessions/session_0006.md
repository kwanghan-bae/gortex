# Session 0006

## Goal
- 외부 기술 트렌드의 지식 베이스화 (Synaptic Knowledge Base v1)

## What Was Done
- **agents/trend_scout.py 수정**: 스캔된 신규 모델 및 기술 패턴 정보를 `LongTermMemory`에 자동 저장하도록 개선. "TrendScout"을 출처로 명시하여 지식의 계보를 확보함.
- **agents/manager.py 수정**: 장기 기억 소환 시 최신 트렌드 지식이 포함되어 있으면 이를 계획 수립에 우선적으로 반영하도록 시스템 프롬프트 보강.
- **utils/vector_store.py 연동**: 기존 텍스트 기반 저장소를 활용하여 지식 조각(Snippets)을 성공적으로 통합함.

## Decisions
- 트렌드 지식은 `Recall` 시점에 별도의 태그(최신/신규)를 통해 에이전트에게 중요성을 환기시키도록 함.
- 모든 지식 저장 시 출처 메타데이터를 필수적으로 포함하여 정보의 신뢰도를 관리함.

## Problems / Blockers
- 현재 지식 저장소가 텍스트 기반 검색(`recall`)에 의존하고 있어, 의미론적 유사도가 낮은 경우 검색에 실패할 수 있음. 향후 임베딩 기반 벡터 검색으로의 전환이 필요함.

## Notes for Next Session
- 지식 베이스가 커짐에 따라, 오래되거나 유효하지 않은 지식을 정리하는 'Knowledge Garbage Collection' 기능이 필요함.
