# Next Session

## 세션 목표
- **Evolutionary Node Realization**: 비어있는 `agents/evolution_node.py`를 정식 구현하여 시스템이 스스로 소스 코드를 분석하고 아키텍처 개선안을 적용하는 자가 진화 루프를 가동한다.
- **Intelligent Model Routing**: `EfficiencyMonitor`에 축적된 데이터를 분석하여, 특정 작업에 대해 가장 효율적인 모델(Ollama vs Gemini)을 자동으로 선택하는 라우팅 엔진 프로토타입 개발.

## 컨텍스트
- 모든 에이전트가 하이브리드 아키텍처로 전환되어 모델 교체가 자유로운 상태입니다.
- 성능 데이터가 축적되기 시작했으므로, 이제는 데이터에 기반한 의사결정이 가능합니다.

## 범위 (Scope)
### 수행할 작업 (Do)
- `agents/evolution_node.py`: 코드 구조 개선 및 패턴 승격을 담당하는 신규 노드 구현.
- `utils/efficiency_monitor.py`: 수집된 데이터를 바탕으로 모델 성능 순위를 반환하는 분석 메서드 추가.
- `core/engine.py`: 에이전트 호출 전 최적 모델을 예측하여 할당하는 가이드 로직 실험.

### 수행하지 않을 작업 (Do NOT)
- 시스템 아키텍처의 근간(Graph 구조)을 사용자 승인 없이 대규모로 파괴하지 않는다.

## 기대 결과
- 시스템이 스스로 성능을 모니터링하고 최적의 리소스를 배분하는 지능형 멀티 에이전트로 한 단계 도약한다.
- 자가 진화 로직을 통해 기술 부채가 자동으로 감지되고 해소되는 환경이 구축된다.

## 완료 기준
- `evolution_node.py` 동작 확인.
- 모델 성능 기반 자동 라우팅 프로토타입 완성.
- `docs/sessions/session_0065.md` 기록.