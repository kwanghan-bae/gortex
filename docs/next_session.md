# Next Session

## 세션 목표
- **Evolution Dashboard Realization**: 시스템의 자가 진화 과정(코드 변경 이력, 성능 점수 추이)을 한눈에 볼 수 있는 시각화 인터페이스를 웹 대시보드에 추가한다.
- **Self-Reinforcement Loop (RLHF-lite)**: `pre-commit` 결과(성공/실패)를 실시간으로 모델 점수에 반영하여, 특정 작업에 약한 모델을 자동으로 기피하도록 학습하는 루프를 가동한다.

## 컨텍스트
- 지능형 라우팅 엔진이 가동 중이나, 아직은 누적 통계에 의존하고 있습니다.
- 실시간 피드백을 통한 즉각적인 점수 조정이 추가되면 더욱 동적인 최적화가 가능해집니다.

## 범위 (Scope)
### 수행할 작업 (Do)
- `ui/evolution_view.py`: 진화 히스토리를 렌더링하는 FastAPI 엔드포인트 및 프론트엔드 코드 작성.
- `agents/evolution_node.py`: 진화 시도 직후 결과를 `EfficiencyMonitor`에 '실시간 가중치'와 함께 기록하는 로직 보강.
- `utils/efficiency_monitor.py`: 즉각적인 피드백을 처리하는 `apply_immediate_feedback` 메서드 추가.

### 수행하지 않을 작업 (Do NOT)
- 복잡한 딥러닝 기반 강화학습 모델을 도입하지 않는다. (통계 기반의 가중치 조정에 집중)

## 기대 결과
- 시스템의 '살아있는' 진화 과정을 시각적으로 증명.
- 작업 실패 경험이 즉시 시스템 지능에 반영되는 자가 개선 속도 향상.

## 완료 기준
- 웹 대시보드 내 Evolution View 동작 확인.
- 실패한 작업에 대해 해당 모델 점수가 즉시 하락하는지 검증.
- `docs/sessions/session_0067.md` 기록.