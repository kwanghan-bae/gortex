# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Speculative Reasoning & Scenario Swarm Complete (v2.0.2)

## 🧠 Current Context
병렬 가설 추론(Speculative Reasoning) 엔진이 성공적으로 안착되었습니다. 이제 Gortex는 하나의 정답을 기다리는 대신, 여러 가능성을 동시에 타진하고 가장 확신도가 높은 최적의 해결책을 선별할 수 있는 고차원적인 지능을 갖추게 되었습니다.

## 🎯 Next Objective
**Synaptic Knowledge Graph (Visual Memory)**
1. **`Knowledge Mapping`**: 인덱싱된 코드 정보(`Synaptic Index`)와 학습된 규칙(`Evolutionary Memory`)을 하나의 거대한 그래프 데이터베이스 구조로 통합합니다.
2. **`Visual Exploration`**: 웹 대시보드에서 이 지식 그래프를 인터랙티브하게 탐색할 수 있는 기능을 구현하여, 시스템이 알고 있는 정보들 사이의 관계를 시각적으로 파악할 수 있게 합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 병렬 가설 추론 엔진 완료 (v2.0.2).
- 다음 목표: 지식 기반 그래프 통합 시각화(Synaptic Knowledge Graph).

작업 목표:
1. `utils/indexer.py`와 `EvolutionaryMemory`의 데이터를 결합하여 통합 지식 그래프(Nodes/Edges)를 생성하는 `generate_knowledge_graph` 기능을 작성해줘.
2. 생성된 그래프 데이터를 웹 대시보드로 스트리밍하고, 노드 간의 논리적 연관성을 시각화하는 기반을 마련해줘.
```