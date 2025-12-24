# Session 0130: Dynamic Swarm Recruitment

## 🎯 Goal
- 복잡하거나 위험한 과제 발생 시, 하드코딩된 가상 페르소나 대신 시스템 내에서 가장 숙련도가 높은 실제 에이전트들을 소집하여 '드림팀(Swarm)'을 구성하는 로직 구현.

## 📈 Outcomes
- **Swarm Agent (agents/swarm.py)**:
    - `recruit_experts`: `Registry`와 `EconomyManager`를 조회하여 요구 스킬(`Security`, `Design` 등)별 최고 득점자를 자동으로 선발하는 로직 구현.
    - `conduct_dynamic_round`: 선발된 전문가의 메타데이터(`Role`, `Description`)를 시스템 프롬프트에 동적으로 주입하여, 각자의 전문 영역에서 토론하도록 개선.
    - Fallback Mechanism: 적절한 전문가가 없을 경우 기존의 정적 페르소나(Innovation vs Stability) 또는 Planner를 보조자로 투입하는 안전장치 마련.
- **Dashboard UI (ui/dashboard.py)**:
    - `update_debate_monitor`: 토론 패널에 참여 에이전트의 실명과 역할(예: `Coder (Developer)`)을 구분하여 표시하고, 전문가에게는 별도의 색상(Green)을 부여하여 시각적 차별화.
- **Verification**:
    - `tests/test_swarm_recruitment.py`: 모의 경제 데이터를 바탕으로 보안 전문가(`Analyst`)와 구현 전문가(`Coder`)가 정확히 소집되는지 검증 완료.

## 🛠️ Technical Decisions
- **Role vs Persona**: 기존에는 'Innovation' 같은 추상적 페르소나였으나, 이제는 `registry.py`에 등록된 `AgentMetadata.role` (예: Auditor, Architect)이 토론의 주체가 됨.
- **Async Testing**: `unittest` 환경에서의 비동기 이벤트 루프 충돌 문제를 해결하기 위해 테스트 코드 내에서 명시적으로 새 루프를 생성하여 격리.

## 🚀 Next Actions
- **Debate Memory Integration**: Swarm 토론에서 도출된 합의안(Consensus)을 `EvolutionaryMemory`에 '초월적 규칙(Super Rule)'으로 저장하여, 시스템 전체의 지능을 영구적으로 향상.
- **Conflict Resolution**: 서로 다른 에이전트가 충돌하는 의견을 낼 때, `Manager`가 개입하여 중재하거나 투표(Voting)로 결정하는 메커니즘 추가.
