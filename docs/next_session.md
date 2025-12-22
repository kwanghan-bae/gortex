# Next Session

## 세션 목표
- **Evolutionary Roadmap Generation**: `Analyst`가 산출한 '지능 지수'가 낮은 모듈과 `TrendScout`이 발견한 '신기술'을 매칭하여, 시스템의 발전을 위한 최적의 우선순위를 담은 '진화 로드맵'을 매 세션마다 자동 생성한다.
- **Cross-Model Peer Review**: `EvolutionNode`가 생성한 코드를 즉시 병합하지 않고, `Analyst` 노드가 다른 LLM 모델(예: Gemini 1.5 Flash vs Pro)을 활용하여 교차 리뷰를 수행한 후 일정 점수 이상일 때만 승인하는 거버넌스를 강화한다.

## 컨텍스트
- 시스템이 스스로 지능 지수를 측정할 수 있게 되었으므로, 이제는 취약한 부분을 전략적으로 공략할 단계입니다.
- 단일 모델의 판단 오류를 방지하기 위해 다중 모델의 집단 지성을 활용한 검증 체계가 필요합니다.

## 범위 (Scope)
### 수행할 작업 (Do)
- `agents/analyst/base.py`: 지능 지수 기반의 진화 우선순위 보고서를 생성하는 `generate_evolution_roadmap` 메서드 추가.
- `agents/analyst/__init__.py`: `EvolutionNode`의 결과물에 대해 다중 모델 리뷰를 수행하는 `perform_peer_review` 로직 구현.
- `agents/manager.py`: 로드맵 정보를 바탕으로 `evolution` 노드로의 라우팅 비중을 조절하는 정책 보강.

### 수행하지 않을 작업 (Do NOT)
- 로드맵 생성 시 이미 지능 지수가 높은 모듈을 과도하게 중복 리팩토링하지 않는다.

## 기대 결과
- '약점 보완' 중심의 전략적인 자가 진화 달성.
- 다중 모델의 교차 검증을 통해 자가 수정 코드의 안정성과 품질 극대화.

## 완료 기준
- 세션 로그에 '진화 로드맵'이 출력되는지 확인.
- `peer_review` 점수가 낮은 코드가 자동으로 반려(Rollback)되는지 검증.
- `docs/sessions/session_0074.md` 기록.