# Next Session

## 세션 목표
- **Evolutionary Dataset Curation**: `Analyst`가 성공한 자가 진화 및 리팩토링 사례(Before/After 코드 쌍)를 선별하여 `logs/datasets/evolution.jsonl` 형식으로 큐레이션하고, 이를 미래의 모델 미세 조정(Fine-tuning) 데이터로 활용할 수 있도록 정비한다.
- **TUI Health Score Visualization**: Rich 라이브러리를 활용하여, 터미널 대시보드 우측 하단에 최근 10세션의 `Health Score` 추이를 보여주는 스파크라인(Sparkline) 또는 소형 그래프를 구현한다.

## 컨텍스트
- 시스템이 이제 '검증된 진화'를 수행하므로, 이 성공 사례들은 시스템의 소중한 자산입니다.
- 건강도 점수를 단순 텍스트가 아닌 '흐름'으로 보여줌으로써 진화의 방향성을 시각적으로 즉시 파악할 수 있게 합니다.

## 범위 (Scope)
### 수행할 작업 (Do)
- `agents/analyst/base.py`: 성공적인 진화 사례를 구조화하여 저장하는 `curate_evolution_data` 메서드 추가.
- `ui/dashboard.py`: 건강도 히스토리 데이터를 시각화하는 `render_health_chart` 로직 보강.
- `utils/efficiency_monitor.py`: 세션별 건강도 점수를 영구 기록하는 필드 추가.

### 수행하지 않을 작업 (Do NOT)
- 단순 버그 수정이나 사소한 변경 사항까지 데이터셋에 포함하여 노이즈를 늘리지 않는다.

## 기대 결과
- 자가 진화 데이터를 스스로 자산화하는 '학습하는 시스템'으로 진화.
- 아키텍처 건강 상태를 직관적으로 관측할 수 있는 고성능 TUI 대시보드 완성.

## 완료 기준
- `evolution.jsonl` 파일에 정제된 데이터가 누적되는지 확인.
- TUI 화면에 건강도 추이 그래프가 정상적으로 렌더링되는지 검증.
- `docs/sessions/session_0079.md` 기록.