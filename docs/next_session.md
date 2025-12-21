# Next Session

## 세션 목표
- `OLLAMA_PLAN.md` 전면 적용 마무리: `agents/manager.py`가 `LLMFactory`를 사용하도록 리팩토링하고, 전체 에이전트 워크플로우에서의 모델 전환 안정성을 검증한다.

## 컨텍스트
- Phase 1(Memory), Phase 2(Coder) 및 TUI 안정화가 완료되었습니다.
- 이제 시스템의 두뇌인 `Manager`가 백엔드 상황에 따라 적절한 모델을 할당하고 조율하는 최종 하이브리드 로직을 완성해야 합니다.

## 범위 (Scope)
### 수행할 작업 (Do)
- `agents/manager.py`: `GortexAuth` 직접 의존성 제거 및 `LLMFactory` 도입.
- **Routing Intelligence**: `OLLAMA_PLAN.md` 원칙(Worker vs Manager)에 따라, 단순 라우팅은 로컬 모델을 고려하고 복잡한 전략 수립은 Gemini를 강제하는 로직 구현.
- **Unified Testing**: `tests/test_manager.py` 업데이트 및 전체 `pytest` 실행을 통한 통합 무결성 확인.

### 수행하지 않을 작업 (Do NOT)
- `Manager`의 복잡한 의도 분석(Intent Projection) 로직을 로컬 모델로 전면 이관하지 않는다. (성능 검증 전까지)

## 기대 결과
- Gortex 시스템 전체가 특정 LLM 공급자에 종속되지 않는 완전한 추상화 상태에 도달한다.
- 하이브리드 모드 운영 시 API 비용 최적화가 극대화된다.

## 완료 기준
- `agents/manager.py` 리팩토링 완료.
- 통합 테스트 통과.
- `docs/sessions/session_0063.md` 기록.