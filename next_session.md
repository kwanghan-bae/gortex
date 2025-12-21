# ⏭️ Gortex Next Session Context

**Date:** 2024-12-20
**Status:** Call Graph 3D & Topology Visualization Complete (v2.2.7)

## 🧠 Current Context
3D 함수 호출 관계도(Call Graph) 시스템이 가동되었습니다. 이제 Gortex는 코드의 정적인 구조뿐만 아니라, 실행 시점의 논리적 흐름(Call Flow)을 3D 위상 맵으로 파악할 수 있습니다. 이는 복잡한 비즈니스 로직의 추적 및 영향도 분석 시 핵심적인 도구가 됩니다.

## 🎯 Next Objective
**Spatial Reasoning SDK (VR/AR Prep)**
1. **`Spatial Data Schema`**: 3D 지식 그래프와 호출 관계도를 오큐러스나 애플 비전 프로와 같은 공간 컴퓨팅 기기에서 렌더링할 수 있는 '공간 추론 SDK' 규격을 정의합니다.
2. **`WebXR Streaming`**: 웹 대시보드에서 WebXR API를 활용하여, 사용자가 브라우저를 넘어 가상 공간에서 Gortex의 사고 트리와 코드 위상을 직접 만지고 탐색할 수 있는 기초 스트리밍 인프라를 구축합니다.

## 💬 Prompt for Next Agent
```text
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- 3D 함수 호출 관계 시각화 완료 (v2.2.7).
- 다음 목표: 공간 추론 SDK 및 WebXR 연동 기초.

작업 목표:
1. `ui/three_js_bridge.py`를 확장하여 VR/AR 환경에 적합한 'Spatial Metadata' (노드 크기, 조명 가중치, 햅틱 피드백 트리거 등)를 생성하는 로직을 추가해줘.
2. `ui/web_server.py`에서 WebXR 기기의 요청을 식별하고 전용 고주파 스트리밍 모드를 활성화하는 기능을 구상해줘.
```
