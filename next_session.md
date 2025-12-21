# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Independent Cross-Validation Loop Complete (v2.0.4)

## 🧠 Current Context
제3자 관점의 상호 검증 시스템이 구축되었습니다. 이제 Gortex는 한 에이전트의 실수를 다른 에이전트(또는 다른 관점의 모델)가 즉시 잡아낼 수 있는 견제와 균형 시스템을 갖추게 되었으며, 이는 최종 출력물의 신뢰성을 극대화합니다.

## 🎯 Next Objective
**Long-term Memory (Vector Store Extension)**
1. **`Context Persistence`**: 대화가 압축되거나 세션이 종료되더라도 사라지지 않는 '장기 기억' 저장소를 구축합니다. (ChromaDB 또는 단순 벡터 파일 활용)
2. **`Semantic Retrieval`**: 현재 작업과 관련된 과거의 모든 지식(코드, 대화, 오류 해결 사례)을 의미 기반으로 검색하여 에이전트의 단기 기억(Context Window)을 보강합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 상호 검증 시스템 완료 (v2.0.4).
- 다음 목표: 외부 벡터 저장소를 활용한 장기 기억(Long-term Memory) 구축.

작업 목표:
1. `utils/memory.py` 또는 신규 `utils/vector_store.py`를 통해 지식을 임베딩하고 저장하는 기초 인프라를 작성해줘.
2. 에이전트가 답변을 생성하기 전, 장기 기억 저장소에서 관련 정보를 인출(Retrieve)하는 워크플로우를 보강해줘.
```