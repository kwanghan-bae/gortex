# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Reviewer Dashboard & Multi-Agent Approval Complete (v2.2.1)

## 🧠 Current Context
다중 에이전트 승인 시스템(Reviewer Dashboard)이 구축되었습니다. 이제 중요한 작업은 여러 에이전트의 검증과 합의를 거쳐야 하며, 이 과정은 웹 대시보드에서 실시간으로 모니터링됩니다. 이는 시스템의 집단 지성을 활용한 품질 제어 능력을 극대화합니다.

## 🎯 Next Objective
**Synaptic Asset Manager (Static Asset Management)**
1. **`Asset Centralization`**: 시스템에서 사용하는 모든 아이콘, 템플릿, 정적 텍스트 에셋들을 중앙 저장소에서 관리합니다.
2. **`Dynamic Asset Loading`**: 테마나 언어 설정에 따라 적절한 에셋을 동적으로 불러와 UI에 적용하며, 새로운 에셋을 시스템 중단 없이 추가할 수 있는 유연한 구조를 구축합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 다중 에이전트 리뷰 보드 완료 (v2.2.1).
- 다음 목표: 중앙 에셋 관리 시스템(Synaptic Asset Manager) 구축.

작업 목표:
1. `utils/asset_manager.py`를 신설하여 아이콘, 시스템 메시지 템플릿 등을 관리하는 `AssetManager` 클래스를 구현해줘.
2. `DashboardUI` 및 `main.py`에서 하드코딩된 문자열이나 아이콘을 `AssetManager`를 통해 로드하도록 리팩토링해줘.
```
