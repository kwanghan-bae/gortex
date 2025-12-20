# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Researcher & Cache Implemented

## 🧠 Current Context
핵심 에이전트 팀(`Manager`, `Planner`, `Coder`, `Researcher`)이 모두 구축되었습니다.
또한 Redis 캐시(`utils/cache.py`)를 통해 성능 최적화 기반을 마련했습니다.
다음 단계는 데이터 분석 및 자가 진화를 위한 피드백 분석을 담당하는 **`Analyst`**입니다.

## 🎯 Next Objective
**Agent Implementation Phase (Self-Evolution Prep)**
1. `gortex/agents/analyst.py`: 두 가지 모드(Data Mode, Evolution Mode)를 가진 에이전트 구현.
   - **Data Mode**: Pandas를 사용하여 CSV/Excel 데이터 분석.
   - **Evolution Mode**: 사용자의 부정적 피드백 원인 분석 및 `experience.json`용 규칙 추출.
2. `gortex/core/evolutionary_memory.py`: `experience.json` 관리 로직 구현 (필요시).

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- Researcher 및 Cache 구현 완료.
- 다음 목표: `agents/analyst.py` 구현.

주의사항:
- Analyst는 Pandas를 사용하여 데이터를 처리해야 함.
- 자가 진화(Evolution)를 위해 사용자의 "아니", "틀렸어" 같은 피드백에서 핵심 제약 조건을 추출하는 로직을 정밀하게 설계할 것.
```
