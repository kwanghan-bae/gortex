# Session 0129: Intelligent Routing & Skill-based Allocation

## 🎯 Goal
- 에이전트의 스킬 등급(Mastery Level)을 고려하여 작업을 가장 적합한 전문가에게 할당하고, 고숙련 에이전트에게는 더 강력한 모델 리소스를 배정하는 지능형 라우팅 시스템 구축.

## 📈 Outcomes
- **Manager Agent (agents/manager.py)**:
    - 라우팅 알고리즘 개선: 단순 총점(Points) 정렬 방식에서 벗어나, 요구 능력(`required_capability`)과 연관된 **특정 스킬 점수**에 70% 가중치를 부여하는 하이브리드 정렬 로직 도입.
    - 결과: `Coding` 작업 시 총점이 낮아도 코딩 실력이 뛰어난 전문가가 선발됨.
- **Gortex Engine (core/engine.py)**:
    - 리소스 할당 정책 고도화: 에이전트의 주력 스킬 점수가 Master 등급(2500점 이상)인 경우, 위험도가 다소 낮더라도 고성능 모델(`gemini-1.5-pro`)을 우선 배정하여 전문성을 극대화.
- **Verification**:
    - `tests/test_intelligent_routing.py`: 스킬 기반 라우팅 및 모델 할당 시나리오 검증 완료 (Pass).

## 🛠️ Technical Decisions
- **Weighted Scoring**: 스킬 점수 100%가 아니라 총점 30%를 반영한 이유는, 전문성이 높더라도 기본 평판(신뢰도)이 너무 낮은 에이전트(예: 갓 생성된 에이전트)가 무조건 선발되는 것을 방지하기 위함.
- **Skill Mapping**: `coding`, `write` 등의 키워드를 `Coding` 스킬로 매핑하는 휴리스틱 로직을 Manager 내부에 구현 (추후 `Registry`로 이동 고려).

## 🚀 Next Actions
- **Swarm Recruitment**: 단일 에이전트로 해결하기 어려운 복합 과제 발생 시, 스킬 기반으로 최적의 'Dream Team'을 구성하는 Swarm 형성 로직 구현.
- **Dynamic Persona Injection**: 선발된 전문가의 스킬 특성(예: "Security Specialist")을 시스템 프롬프트에 동적으로 주입하여 말투와 사고 방식을 강화.
