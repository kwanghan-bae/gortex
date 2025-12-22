# Next Session

## 세션 목표
- **Incremental Architecture Refactoring**: `EvolutionNode`가 로드맵의 'High Priority' 항목을 단순히 수정하는 것을 넘어, 관련된 의존성 파일을 한꺼번에 분석하여 서브시스템 전체의 아키텍처를 일관성 있게 개선하는 '다중 파일 진화 루프'를 가동한다.
- **Dynamic Persona Evolution**: 성공적인 작업 패턴과 실패한 피드백을 분석하여, 각 에이전트의 성격 정의(`docs/i18n/personas.json`)를 시스템이 스스로 튜닝하고 보강하는 '성격의 자가 진화' 기능을 구현한다.

## 컨텍스트
- 개별 파일 단위의 진화는 안정 궤도에 올랐으나, 아키텍처적 완성도를 위해서는 모듈 간의 연계 수정이 필수적입니다.
- 에이전트의 페르소나가 고정되어 있으면 진화하는 기술 환경에 뒤처질 수 있으므로, 성격 자체도 데이터 기반으로 업데이트되어야 합니다.

## 범위 (Scope)
### 수행할 작업 (Do)
- `agents/evolution_node.py`: 단일 파일 수정을 넘어 영향 범위(`Impact Radius`) 전체를 분석하여 대규모 수정을 제안하는 로직 보강.
- `agents/analyst/base.py`: 에이전트 성과 데이터를 바탕으로 페르소나 지침 개선안을 생성하는 `evolve_personas` 메서드 추가.
- `docs/i18n/personas.json`: 시스템에 의해 자동 업데이트되는 'Self-Tuned Persona' 섹션 추가.

### 수행하지 않을 작업 (Do NOT)
- 시스템의 기본 성격(Innovation vs Stability)의 근간을 사용자 승인 없이 완전히 파괴하지 않는다.

## 기대 결과
- 파편화된 리팩토링이 아닌, 구조적 통일성을 갖춘 대규모 시스템 진화 달성.
- 각 작업 맥락에 더 민감하고 전문화된 '진화하는 에이전트' 성격 구축.

## 완료 기준
- 다중 파일 수정 시나리오가 `pre-commit`을 통과하는지 확인.
- `personas.json` 파일이 성능 데이터에 따라 자동으로 보강되는지 검증.
- `docs/sessions/session_0075.md` 기록.