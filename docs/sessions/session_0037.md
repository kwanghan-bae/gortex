# Session 0037

## Goal
- 3D 의존성 군집화 및 클러스터 시각화 (Dependency Clustering v1)

## What Was Done
- **ui/three_js_bridge.py 수정**: 
    - 파일 경로나 심볼 이름의 패턴을 분석하여 노드들을 논리적 그룹으로 묶는 `apply_clustering` 메서드 구현.
    - 각 노드에 `cluster_id`와 고유한 `cluster_color`(해시 기반)를 부여하여 시각적 구별 기반 마련.
    - `convert_causal_graph_to_3d` 및 `convert_kg_to_3d` 반환 직전에 클러스터링을 자동 적용하도록 연동.
- **Bug Fix**: 이전 작업 중 누락되었던 `convert_kg_to_3d` 메서드를 최신 로직(Knowledge Mapping 포함)으로 복구.

## Decisions
- 가독성을 극대화하기 위해 파일 시스템 계층 구조(예: core/, agents/, utils/)를 우선적인 클러스터링 기준으로 채택함.
- 클러스터 색상은 ID의 해시값을 활용하여 자동으로 생성함으로써, 새로운 모듈이 추가되어도 별도의 설정 없이 고유 색상이 할당되도록 설계함.

## Problems / Blockers
- 현재 클러스터링은 1단계 깊이의 단순 패턴 매칭임. 향후 복잡한 의존성 밀도(Density) 분석을 통한 '동적 커뮤니티 감지(Community Detection)' 알고리즘 도입 시 더욱 정교한 그룹화가 가능할 것으로 보임.

## Notes for Next Session
- 시스템의 '언어적 유연성'을 완성하기 위해, 현재 에이전트들이 사용하는 모든 텍스트 메시지(로그, 상태 보고 등)를 타겟 언어(한국어/영어 등)에 맞게 런타임에 동적으로 치환하는 'System-wide Localization'이 필요함.
