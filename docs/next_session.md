# Next Session

## 세션 목표
- **Global Constraint Synthesis**: 분산되어 저장된 수많은 미시적 규칙(experience.json)을 `Analyst`가 정기적으로 고차원적인 '시스템 가이드라인'으로 승격시키고, 이를 `docs/RULES.md`에 자동으로 반영하는 전역 지식 통합 루프를 가동한다.
- **Model-Persona Affinity Mapping**: `EfficiencyMonitor` 데이터를 활용하여, 페르소나별(Innovation vs Stability) 및 작업별(Arch vs Code)로 가장 성과가 좋았던 모델을 매핑하고, `Manager`가 이를 바탕으로 '전문가 모델'을 강제 할당하는 로직을 고도화한다.

## 컨텍스트
- 시스템이 개별적인 실수는 잘 교정하고 있으나, 이를 거시적인 원칙으로 승격시키는 과정은 아직 수동적입니다.
- 데이터가 충분히 쌓였으므로, 이제는 모델의 '이름'이 아닌 '실제 성과'를 바탕으로 한 전문가 할당 체계로 넘어가야 합니다.

## 범위 (Scope)
### 수행할 작업 (Do)
- `agents/analyst/base.py`: 미시적 규칙들을 요약하여 거시적 원칙을 추출하는 `synthesize_global_rules` 메서드 추가.
- `utils/efficiency_monitor.py`: '모델별 페르소나 적합도' 점수를 산출하는 분석 메서드 구현.
- `docs/RULES.md`: 에이전트에 의해 자동 업데이트되는 'Auto-Evolved Rules' 섹션 추가.

### 수행하지 않을 작업 (Do NOT)
- 사용자가 명시적으로 정한 핵심 보안 원칙을 LLM이 임의로 삭제하게 두지 않는다.

## 기대 결과
- 파편화된 지식이 체계적인 원칙으로 진화하는 '지능의 구조화' 달성.
- 각 작업에 가장 특화된 모델이 즉시 투입되는 '최적의 전문가 함대' 가동.

## 완료 기준
- `experience.json`의 내용이 요약되어 `docs/RULES.md`에 자동 반영되는지 확인.
- 작업 성격에 따라 모델 할당이 통계적으로 유의미하게 변하는지 검증.
- `docs/sessions/session_0071.md` 기록.