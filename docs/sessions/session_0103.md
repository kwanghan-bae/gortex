# Session 0103: Dynamic Agent Orchestration & Capability Discovery

## 📅 Date
2025-12-23

## 🎯 Goal
- **Dynamic Agent Orchestration & Capability Discovery**: 에이전트의 이름을 직접 지정하는 하드코딩 방식에서 벗어나, 필요한 '능력(Capability)'을 기반으로 레지스트리에서 최적의 에이전트를 실시간으로 탐색하여 연결하는 지능형 라우팅 구현.

## 📝 Activities
### 1. Semantic Agent Discovery
- `core/registry.py`: `get_agents_by_tool` 및 `get_agents_by_role` 유틸리티 추가. 도구 명칭이나 역할 이름으로 에이전트를 검색할 수 있는 인덱스 구축.
- `manager_node`: 사용자의 의도에서 "무엇이 필요한가(required_capability)"를 추출하고, 이를 레지스트리에 질의하여 타겟 노드를 결정하도록 로직 전면 개편.

### 2. Reputation-based Selection
- 동일한 능력을 가진 에이전트가 여러 명일 경우, `agent_economy`의 평판 점수가 가장 높은 에이전트를 우선적으로 선택하는 '실력 중심 할당' 알고리즘 적용.

### 3. Integrated Resource Strategy
- Session 0099에서 구축한 '일일 예산 기반 모델 스케일링'을 `Manager`의 최종 결정 단계에 통합하여, 성능과 비용의 최적 균형점을 자율적으로 탐색.

### 4. Verification
- `tests/test_dynamic_orchestration.py`: 새로운 `Deployer` 에이전트를 레지스트리에 등록한 뒤, 사용자의 배포 요청 시 `Manager`가 코드 수정 없이도 해당 에이전트를 정확히 찾아내어 라우팅하는지 검증 완료.

## 📈 Outcomes
- **Decoupled Architecture**: 에이전트 추가 시 `graph.py`나 `manager.py`를 수정할 필요가 없는 완전한 플러그인 체계 안착.
- **Intelligence Flexibility**: 시스템이 직면한 과제에 대해 가장 적합한 전문가(에이전트)를 스스로 임명하는 고차원적 오케스트레이션 지능 확보.

## ⏭️ Next Steps
- **Session 0104**: v3.0 Interactive Dashboard Upgrade.
- TUI 대시보드에 레지스트리에 등록된 에이전트 목록과 그들의 전문 분야(스킬)를 실시간으로 노출하고, 현재 수행 중인 '능력'을 강조하는 시각화 강화.
