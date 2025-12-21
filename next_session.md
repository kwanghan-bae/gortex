# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Code Explainer & Logic Analysis Complete (v2.1.6)

## 🧠 Current Context
비즈니스 로직 설명 엔진이 구축되었습니다. 이제 Gortex는 코드를 작성하는 기술적인 단계를 넘어, 작성된 코드의 의미와 파급 효과를 인간의 언어로 상세히 설명할 수 있습니다. 이는 특히 유지보수 과정에서 신규 투입 인력이나 비기술 이해관계자와의 소통을 획기적으로 돕습니다.

## 🎯 Next Objective
**Causal Tracking (Decision Lineage)**
1. **`Decision Lineage`**: 시스템 내부에서 특정 결정(예: 모델 변경, 특정 파일 수정)이 내려진 근본적인 원인과 그 파생 효과를 추적하여 '인과 관계 그래프'로 기록합니다.
2. **`Visual Causal Map`**: 웹 대시보드에서 특정 성과나 오류를 클릭하면, 해당 결과에 도달하기까지의 사고 체인(Decision Chain)을 역순으로 시각화하여 보여주는 'Root-Cause Analysis' 기능을 구현합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 코드 로직 설명 엔진 완료 (v2.1.6).
- 다음 목표: 의사결정 인과 관계 추적 시스템(Causal Tracking).

작업 목표:
1. `core/observer.py` 또는 `DashboardUI`를 확장하여 노드 간의 결정 인과 관계(parent_decision_id 등)를 저장하는 기능을 추가해줘.
2. 특정 결과물의 '족보(Lineage)'를 추적하여 그래프 데이터로 반환하는 로직을 작성해줘.
```