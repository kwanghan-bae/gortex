# Session 0034

## Goal
- 핵심 설계 의사결정 및 컨텍스트 자동 고정 (Context Pinning v1)

## What Was Done
- **core/state.py 수정**: 삭제 대상에서 제외될 핵심 컨텍스트를 보관하는 `pinned_messages` 필드 추가.
- **utils/memory.py 수정**: 메시지 가지치기(`prune_synapse`) 시 `pinned_messages`를 최상단에 배치하여 중요한 결정 사항의 영구 보존 보장.
- **agents/manager.py 수정**: 중요한 아키텍처 결정이나 정책 확정 시 에이전트가 스스로 `pin_this`를 요청할 수 있도록 응답 스키마 확장 및 지침 보강.
- **main.py 연동**: 에이전트의 고정 요청(`pin_this`)을 포착하여 `pinned_messages`에 자동 축적하는 루프 구현.

## Decisions
- 컨텍스트 고정은 에이전트의 자율적 판단(`pin_this`)에 맡기되, 중복 저장을 방지하여 토큰 효율성을 유지함.
- `pinned_messages`는 모든 세션 요약보다도 앞선 최상단(X-ray 계층)에 위치하여 추론의 기초가 됨.

## Problems / Blockers
- 현재 고정된 메시지가 너무 많아질 경우 실제 작업 공간(메시지 리스트)이 부족해질 수 있음. 향후 고정 메시지에 대해서도 '중요도 기반 우선순위' 또는 '사용자 수동 해제' 기능 도입 고려 필요.

## Notes for Next Session
- 시스템의 '물리적 최적화'를 완성하기 위해, 현재 `file_cache`에 저장되는 파일 해시 정보를 활용하여 변경된 파일만 골라 테스트하고 빌드하는 'Incremental Workflow Support' 기능이 필요함.
