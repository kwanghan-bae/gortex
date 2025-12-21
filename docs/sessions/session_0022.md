# Session 0022

## Goal
- 의미 기반 벡터 검색 엔진 도입 (Vector Search v1)

## What Was Done
- **utils/vector_store.py 수정**: Gemini Embedding API(`models/embedding-001`)를 통합하여 지식 저장 시 벡터화를 자동 수행하도록 개선.
- **의미 검색 구현**: 키워드 매칭 방식에서 코사인 유사도(Cosine Similarity) 기반의 의미론적 검색 방식으로 `recall` 로직 교체.
- **GortexAuth 고도화**: 외부 모듈에서 안전하게 Gemini 클라이언트에 접근할 수 있도록 `get_current_client()` 메서드 추가.
- **테스트 환경 대응**: Mock 객체로 인한 JSON 직렬화 오류 방지를 위해 `TrendScout` 내 데이터 처리 로직을 더 방어적이고 정직한 원문 보존 방식으로 수정.

## Decisions
- 임베딩 API 호출 실패 시 0-벡터(Zero-vector)로 폴백하여 시스템 가용성을 유지하고, 검색 시에는 키워드 매칭이 보조적으로 작동하도록 함.
- 텍스트 파싱 오류 시 가짜 데이터를 생성하지 않고 원문을 그대로 반환하여 데이터 투명성을 확보함.

## Problems / Blockers
- 현재 벡터 유사도 계산을 위해 외부 라이브러리(`numpy` 등) 없이 순수 파이썬으로 구현함. 지식 데이터가 수만 건 이상으로 늘어날 경우 성능 저하가 우려되므로 향후 전용 벡터 라이브러리 도입 검토 필요.

## Notes for Next Session
- 시스템의 '기억 검색'이 강력해졌으므로, 이제 에이전트들이 작업 도중 발생한 모든 사고 과정을 요약하여 장기 기억에 능동적으로 저장하고 나중에 다시 꺼내 쓰는 'Thought Memorization' 기능을 강화해야 함.
