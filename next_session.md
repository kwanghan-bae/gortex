# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Coder Agent Implemented

## 🧠 Current Context
시스템의 손발인 `Coder`까지 구현되었습니다. 이제 Gortex는 계획을 세우고(Plan), 코드를 작성 및 수정(Code & Fix)할 수 있습니다.
다음 단계는 외부 정보를 수집하여 에이전트의 지식을 확장하는 **`Researcher`**입니다.

## 🎯 Next Objective
**Agent Implementation Phase (Complete Core Team)**
1. `gortex/agents/researcher.py`: Playwright를 사용하여 웹에서 정보를 수집하는 에이전트.
   - `SPEC.md`의 성능 최적화(리소스 차단) 및 타임아웃 설정을 준수해야 함.
   - `utils/cache.py` (Redis) 연동 필요 (구현 필요).

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- Coder 구현 완료.
- 다음 목표: `agents/researcher.py` 구현 및 `utils/cache.py` 구현.

주의사항:
- Researcher는 Playwright 사용 시 이미지/폰트 로딩을 차단하여 속도를 높여야 함.
- 검색 결과는 Redis(`utils/cache.py`)에 캐싱하여 중복 호출을 방지할 것.
```