# Next Session

## 세션 목표
- **Architecture Bottleneck Prediction**: `Analyst`가 과거의 `Health Score` 이력을 분석하여, 현재의 코드 수정 패턴이 지속될 경우 3세션 이내에 발생할 '아키텍처 위기 지점'을 미리 예측하고 보고하는 선제적 방어 루프를 가동한다.
- **Persona Success Feedback Loop**: 임시로 창조된 가상 페르소나가 수행한 작업의 성공률(`EfficiencyMonitor` 기반)을 평가하여, 고득점을 획득한 지침을 `docs/i18n/personas.json`에 자동으로 병합하는 '성격의 자연 선택' 기능을 구현한다.

## 컨텍스트
- 시스템이 현재의 건강도를 측정할 수 있게 되었으므로, 이제는 과거 데이터를 바탕으로 '미래'를 예측할 단계입니다.
- 일시적으로 생성된 좋은 아이디어(가상 페르소나 지침)를 영구적인 지식으로 승격시켜야 합니다.

## 범위 (Scope)
### 수행할 작업 (Do)
- `agents/analyst/base.py`: 건강도 추이를 분석하여 병목을 예측하는 `predict_architectural_bottleneck` 메서드 추가.
- `utils/efficiency_monitor.py`: 특정 페르소나 지침의 성공 여부를 별도로 기록하는 메타데이터 필드 보강.
- `agents/manager.py`: 가상 페르소나의 성과를 `Analyst`에게 보고하여 영구 반영 여부를 묻는 핸들러 추가.

### 수행하지 않을 작업 (Do NOT)
- 예측 데이터가 불충분할 때 무리한 리팩토링을 강제하지 않는다.

## 기대 결과
- 사후 처리가 아닌, '사전 예방' 중심의 지능형 아키텍처 관리 달성.
- 성공적인 대처 능력이 시스템의 공식 성격으로 정착되는 자가 발전 메커니즘 완성.

## 완료 기준
- 건강도 하락 추세 감지 시 선제적 리팩토링 제안이 출력되는지 확인.
- 우수 가상 페르소나 지침이 `personas.json`에 반영되는지 검증.
- `docs/sessions/session_0077.md` 기록.