# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Causal Tracking & Decision Lineage Complete (v2.1.7)

## 🧠 Current Context
의사결정 인과 관계 추적 시스템이 가동되었습니다. 이제 Gortex는 모든 결과물에 대해 그 근원이 되는 판단과 행동을 역추적할 수 있는 '족보'를 가집니다. 이는 시스템의 책임성을 높이고 복잡한 오류의 원인을 정밀하게 진단하는 데 핵심적인 자산이 됩니다.

## 🎯 Next Objective
**Root Cause Tree Visualization**
1. **`RCA Tree Logic`**: 특정 이벤트 ID를 기준으로 해당 지점까지 도달한 모든 인과 관계를 트리 구조로 재구성하는 로직을 구현합니다.
2. **`Visual RCA`**: 웹 대시보드에서 특정 로그나 성과를 클릭하면, 그 원인이 된 사고 체인을 역순으로 화려한 애니메이션과 함께 시각화하여 보여주는 전용 뷰를 구축합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 인과 관계 추적 데이터 시스템 완료 (v2.1.7).
- 다음 목표: 근본 원인 분석 트리(Root Cause Tree) 시각화.

작업 목표:
1. `core/observer.py` 또는 `DashboardUI`에 특정 `event_id`의 계보를 추적하여 트리 데이터를 생성하는 `get_causal_chain` 메서드를 작성해줘.
2. 웹 대시보드로 이 체인 데이터를 스트리밍하고, 노드 간의 인과 관계를 시각적으로 표현하는 기능을 보강해줘.
```
