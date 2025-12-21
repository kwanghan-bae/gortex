# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** File Time Machine & Versioning Complete (v2.2.3)

## 🧠 Current Context
파일 버전 관리 시스템(File Time Machine)이 안착되었습니다. 이제 Gortex가 수행한 모든 코드 변경 사항은 기록으로 남으며, 실수로 인한 유실이나 예기치 못한 부작용 발생 시 `/rollback`을 통해 즉시 안전한 상태로 되돌릴 수 있습니다.

## 🎯 Next Objective
**Semantic Code Search (Natural Language Queries)**
1. **`Code Semantics`**: 단순 키워드 검색을 넘어, 코드의 의도와 기능을 자연어로 검색합니다. (예: "결제 관련 로직이 어디 있지?", "데이터베이스 연결 설정 찾아줘")
2. **`Embedding Search`**: 인덱싱된 모든 코드 심볼(함수, 클래스)의 독스트링과 본문을 임베딩하여 벡터 검색을 수행함으로써, 명확한 파일명을 모를 때도 최적의 구현 위치를 찾아냅니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 파일 타임머신 및 버전 관리 완료 (v2.2.3).
- 다음 목표: 자연어 기반 코드 의미 검색(Semantic Code Search) 고도화.

작업 목표:
1. `utils/indexer.py`에 임베딩 벡터 기반의 유사도 검색 기능을 추가하거나, 기존 `SynapticSearch`의 랭킹 로직을 강화해줘.
2. `main.py`의 `/search` 명령어가 더 지능적인 결과를 내도록 프롬프트 기반의 쿼리 정규화 기능을 보강해줘.
```
