# Session 0101: Gortex v3.0 Architecture Design

## 📅 Date
2025-12-23

## 🎯 Goal
- **Gortex v3.0 Architecture Design**: 하드코딩된 에이전트 구조를 탈피하여, 플러그인처럼 에이전트를 동적으로 관리할 수 있는 '중앙 레지스트리' 기반의 차세대 아키텍처 설계 및 기초 구현.

## 📝 Activities
### 1. Central Agent Registry
- `core/registry.py` 신설: 에이전트의 클래스와 메타데이터(이름, 역할, 버전, 가용 도구)를 관리하는 `AgentRegistry` 구현.
- `AgentMetadata` 클래스를 통해 에이전트의 능력을 정형화하여 기술할 수 있는 체계 마련.

### 2. Standard Agent Interface
- `agents/base.py` 신설: 모든 v3.0 에이전트가 상속받아야 할 추상 베이스 클래스 `BaseAgent` 정의.
- `metadata` 속성과 `run` 메서드를 강제하여 일관된 인터페이스 확보.
- LangGraph 노드와의 호환성을 위해 `__call__` 매직 메서드 지원.

### 3. Technical Blueprint Update
- `docs/TECHNICAL_SPEC.md` 개정: v3.0의 핵심인 '탈중앙화 에이전트 로딩' 및 '능력 기반 탐색(Capability Discovery)' 메커니즘을 명문화함.

### 4. Verification
- `tests/test_agent_registry.py`를 통해 가상 에이전트(MockBot)의 등록, 메타데이터 조회, 특정 도구 가용 여부에 따른 에이전트 자동 탐색 기능 검증 완료.

## 📈 Outcomes
- **Extensibility**: 코드 수정 없이 새로운 에이전트를 시스템에 주입할 수 있는 유연한 기반 확보.
- **Modularity**: 에이전트 간의 의존성을 줄이고 개별 에이전트의 버전을 독립적으로 관리할 수 있는 구조적 토대 마련.

## ⏭️ Next Steps
- **Session 0102**: Migration of Core Agents to v3.0.
- `Coder`, `Planner`, `Analyst` 등 기존의 함수 기반 에이전트들을 `BaseAgent`를 상속받는 클래스 구조로 리팩토링하고 레지스트리에 공식 등록함.
