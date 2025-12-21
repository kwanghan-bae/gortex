# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Resource Profiler & Complexity Analysis Complete (v2.2.6)

## 🧠 Current Context
코드 자원 프로파일러가 도입되어 이제 Gortex는 자신이 작성한 코드의 성능적 파급 효과를 정량적으로 파악할 수 있습니다. 이는 단순히 돌아가는 코드를 넘어, 대규모 데이터셋에서도 효율적으로 작동하는 '최적화된 코드'를 지향하는 기초가 됩니다.

## 🎯 Next Objective
**Call Graph 3D (Topology Visualization)**
1. **`Call Relationship Extraction`**: `Synaptic Index`를 확장하여 함수 간의 호출 관계(Call Graph)를 전수 추출합니다.
2. **`3D Topology`**: 웹 대시보드에서 Three.js를 활용하여 프로젝트 전체의 함수 호출 흐름을 3D 위상 맵(Topology Map)으로 시각화합니다. 특정 함수를 클릭하면 해당 함수가 호출하는(Callee) 노드와 해당 함수를 호출하는(Caller) 노드들이 하이라이트되는 인터랙티브 기능을 구현합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 코드 자원 프로파일러 완료 (v2.2.6).
- 다음 목표: 3D 함수 호출 관계도(Call Graph 3D) 시각화.

작업 목표:
1. `utils/indexer.py`를 확장하여 함수 본문 내의 호출 구문을 분석하고 `call_graph` 데이터를 생성하는 로직을 추가해줘.
2. `ui/three_js_bridge.py`를 수정하여 추출된 호출 관계를 3D 공간의 유향 그래프(Directed Graph)로 변환하는 기능을 보강해줘.
```