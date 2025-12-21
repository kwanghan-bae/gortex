# Next Session

## Session Goal
- 동적 메모리 최적화 및 토큰 절약 (Dynamic Memory Pruning v1)

## Context
- `file_cache`와 `messages` 리스트가 세션이 길어질수록 비대해지며, 이는 LLM 호출 비용 상승과 레이턴시 증가로 이어짐.
- 현재 작업 목표와 무관한 파일 캐시를 제거하고, 오래된 메시지를 단순히 요약하는 수준을 넘어 '핵심 변수와 상태'만 남기고 Pruning(가지치기)하는 메커니즘이 필요함.

## Scope
### Do
- `utils/memory.py`를 확장하여 토큰 한계 임박 시 덜 중요한 메시지를 삭제하는 `prune_messages` 로직 추가.
- `main.py`에서 매 턴마다 `file_cache`의 크기를 점검하고, 최근 5턴간 사용되지 않은 파일을 캐시에서 제거하는 LRU(Least Recently Used) 방식 도입.
- 최적화 전후의 토큰 절감량을 USAGE STATS 패널에 보고.

### Do NOT
- 현재 실행 중인 계획(`plan`)과 관련된 데이터는 절대로 삭제 금지.

## Expected Outputs
- `utils/memory.py`, `main.py` 수정.

## Completion Criteria
- 긴 세션 진행 후에도 토큰 사용량이 일정 수준 이하로 유지되고, 불필요한 캐시가 정리되는 것이 확인되어야 함.