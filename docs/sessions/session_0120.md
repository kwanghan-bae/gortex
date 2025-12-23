# Session 0120: Intelligent Task Prioritization & Preemptive Scheduling

## 📅 Date
2025-12-23

## 🎯 Goal
- **Intelligent Task Prioritization & Preemptive Scheduling**: 작업의 긴급도와 가치를 스스로 평가하여 실행 순서를 최적화하고, 리소스 상태에 따라 저가치 작업을 선별적으로 제어하는 전략적 스케줄링 구축.

## 📝 Activities
### 1. Priority-Aware Planning
- `agents/planner.py`: 각 작업 단계(`step`)에 `category` (Security, Fix, Feature, Doc, Refactor)와 `priority_score` (1-10) 필드 추가.
- **Enhanced Persona**: Planner가 단순 순서가 아닌 시스템 임팩트 기반으로 우선순위를 산출하도록 프롬프트 지침 강화.

### 2. Strategic Step Reordering
- `PlannerAgent.run`: 수립된 계획을 `priority_score` 내림차순으로 재정렬하는 엔진 안착. 
- 원래의 논리적 흐름을 유지하기 위해 `id`를 보조 정렬 키로 사용하여 정렬의 안정성 확보.

### 3. Energy-Based Pruning
- **Preemptive Cleanup**: 시스템 에너지 30% 미만 시, 우선순위가 낮은 'Doc' 카테고리 작업을 계획에서 자동 소거하여 가용 자원을 핵심 작업에 집중.

### 4. Verification
- `tests/test_task_prioritization.py`: 긴급 보안 작업의 최우선 배치 및 에너지 위기 시의 저가치 작업 제거 로직 검증 완료.

## 📈 Outcomes
- **Strategic Execution**: 시스템이 더 똑똑하게 무엇을 먼저 해야 할지 판단함으로써 중단 없는 고품질 개발 가능.
- **Fail-Safe Efficiency**: 자원 위기 상황에서도 시스템 붕괴 없이 최소한의 핵심 기능을 유지하는 생존 지능 확보.

## ⏭️ Next Steps
- **Session 0121**: Proactive Dependency Visualization & Impact Mapping.
- 리팩토링이나 대규모 코드 수정 전, 변경이 영향을 주는 의존성 트리를 시각화하고 잠재적 사이드 이펙트를 사전에 리포트하는 '영향력 지도' 엔진 구현.
