# Next Session

## Session Goal
- 의미 기반 벡터 검색 엔진 도입 (Vector Search v1)

## Context
- 현재 `LongTermMemory`와 `SemanticLogSearch`가 단순 키워드 매칭에 의존하고 있어, 표현이 다를 경우 관련 지식을 찾지 못하는 한계가 있음.
- `Sentence-Transformers` 또는 Gemini 임베딩 API를 활용하여 지식을 벡터화하고, 코사인 유사도(Cosine Similarity)를 통해 의미론적으로 유사한 정보를 검색해야 함.

## Scope
### Do
- `utils/vector_store.py`를 확장하여 지식 저장 시 임베딩(Embedding) 벡터를 함께 보관하도록 수정.
- `recall` 메서드를 키워드 매칭에서 벡터 유사도 기반 검색으로 교체.
- 외부 라이브러리 부재 시를 대비한 안전한 폴백(Keyword Match) 유지.

### Do NOT
- 대규모 벡터 DB(Chroma 등)를 즉시 도입하지 말 것 (우선 로컬 JSON 기반 벡터 저장으로 시작).

## Expected Outputs
- `utils/vector_store.py`, `requirements.txt` 수정.

## Completion Criteria
- "데이터 시각화 방법"이라고 물었을 때, "Plotly 활용 가이드"와 같이 키워드가 겹치지 않더라도 의미가 유사한 지식이 검색되는 것이 확인되어야 함.