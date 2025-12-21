# Next Session

## 세션 목표
- `OLLAMA_PLAN.md` 전면 적용 확대: `Planner`, `Researcher`, `Analyst` 에이전트가 `LLMFactory`를 사용하도록 리팩토링하여 시스템 전체의 하이브리드 LLM 아키텍처를 완성한다.
- **Efficiency Benchmarking**: 로컬 모델(Ollama)과 클라우드 모델(Gemini) 간의 작업 성공률 및 비용 대비 성능을 비교할 수 있는 기초 벤치마킹 유틸리티 개발.

## 컨텍스트
- `Coder` 및 `Manager`의 리팩토링이 완료되어 핵심 제어 흐름에 하이브리드 전략이 성공적으로 안착되었습니다.
- `pre-commit` 무한 루프 이슈가 해결되어 자동화된 품질 검증 환경이 안정화되었습니다.

## 범위 (Scope)
### 수행할 작업 (Do)
- `agents/planner.py`, `agents/researcher.py`, `agents/analyst/base.py`: `LLMFactory` 도입 및 응답 파싱 로직 표준화.
- `utils/efficiency_monitor.py` (신규): 모델별 토큰 사용량 및 성공/실패 여부를 추적하는 경량 모니터링 모듈 설계.
- 전체 테스트 커버리지 유지 및 `scripts/pre_commit.sh` 안정성 확인.

### 수행하지 않을 작업 (Do NOT)
- 에이전트 로직 자체의 대규모 기능 변경은 지양하고, LLM 연동 방식의 추상화에 집중한다.

## 기대 결과
- 모든 에이전트가 단일 인터페이스(`LLMFactory`)를 통해 모델에 접근하게 된다.
- 로컬 LLM 운영의 실질적인 이득을 수치화할 수 있는 기반이 마련된다.

## 완료 기준
- 잔여 주요 에이전트 리팩토링 완료.
- 통합 테스트 통과.
- `docs/sessions/session_0064.md` 기록.