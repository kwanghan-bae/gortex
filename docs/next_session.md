# Next Session

## 세션 목표
- **Architecture Drift Guard**: `Analyst`가 정기적으로 소스 코드 간의 의존성 그래프(Dependency Graph)를 추출하여, 자가 진화 과정에서 발생하는 '계층 파괴'나 '순환 참조'를 감지하고 경고하는 방어 로직을 가동한다.
- **Synaptic Memory Pruning**: `EvolutionaryMemory`에 쌓인 학습 규칙들을 LLM이 주기적으로 리뷰하여, 중복되거나 서로 충돌하는 지침을 통합/삭제하는 메모리 압축 루프를 구현한다.

## 컨텍스트
- 시스템의 자율성이 높아질수록 엔트로피(무질서)가 증가할 위험이 있습니다.
- 아키텍처 가이드라인을 엄격히 준수하면서도 진화할 수 있도록 정적 분석 기반의 감시 체계가 필요합니다.

## 범위 (Scope)
### 수행할 작업 (Do)
- `utils/indexer.py`: 클래스/함수 간 호출 관계를 분석하여 의존성 맵을 생성하는 메서드 추가.
- `agents/analyst/base.py`: 의존성 맵을 바탕으로 아키텍처 규칙 위반을 감지하는 `audit_architecture` 로직 구현.
- `core/evolutionary_memory.py`: 규칙 간의 유사도를 분석하여 압축 대상을 식별하는 `prune_memory` 메서드 추가.

### 수행하지 않을 작업 (Do NOT)
- 단순 호출 횟수만으로 중요한 규칙을 삭제하지 않는다. (LLM의 의미론적 판단 중시)

## 기대 결과
- 자가 진화의 속도를 유지하면서도 프로젝트의 구조적 견고함(Code Health) 유지.
- 기하급수적으로 늘어나는 학습 데이터를 핵심 지식 위주로 정제하여 추론 효율성 극대화.

## 완료 기준
- 아키텍처 규칙 위반(예: utils가 agents를 참조) 감지 시 경고 발생 확인.
- `EvolutionaryMemory` 내 중복 규칙 통합 완료.
- `docs/sessions/session_0069.md` 기록.