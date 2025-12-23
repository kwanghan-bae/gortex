# Session 0118: Intelligent Model Selection & Context Budgeting

## 📅 Date
2025-12-23

## 🎯 Goal
- **Intelligent Model Selection & Context Budgeting**: 에이전트 역량, 작업 위험도, 일일 토큰 예산을 종합 분석하여 하이브리드 LLM(Gemini + Ollama) 자원을 최적으로 배분하는 지능형 오케스트레이션 구축.

## 📝 Activities
### 1. Daily Token Budget Tracking
- `utils/token_counter.py`: `DailyTokenTracker` 구현. `logs/token_budget.json`을 통해 날짜별 누적 토큰량과 예상 비용을 추적. 날짜 변경 시 자동 초기화 및 예산 소모율(Status) 계산 기능 탑재.

### 2. Dynamic Model Orchestrator
- `core/engine.py`: `select_optimal_model` 메서드 안착. 
    - **Epic Tasks**: 평판 1000점 이상의 에이전트가 고위험(`risk_score > 0.8`) 작업 시 Gemini Pro 할당.
    - **Budget Guard**: 예산 80% 소모 시 강제 Ollama(로컬) 모드 전환으로 비용 방어.
    - **Cost-Efficiency**: 일반 작업에는 Gemini Flash 또는 Ollama를 우선 배정.

### 3. Integrated Feedback Loop
- 노드 실행 완료 시마다 `process_node_output`을 통해 실제 소모된 토큰량을 추적기에 반영하여 실시간 예산 감시 루프 완성.

### 4. Verification
- `tests/test_model_selection.py`: 예산 임계치 도달 시의 다운그레이드 정책 및 역량 기반의 차등 모델 할당 정합성 검증 완료.

## 📈 Outcomes
- **Resource Efficiency**: 고비용 모델 사용을 정당한 '에픽 작업'으로 한정하여 경제적인 시스템 운영 가능.
- **Sustainability**: API 할당량 소진 시에도 로컬 모델로 즉시 전환하여 시스템 중단 방지.

## ⏭️ Next Steps
- **Session 0119**: Intelligent Resource Scaling & Dynamic Concurrency.
- 작업 대기열의 병목 현상을 감지하여 에이전트 실행 노드를 동적으로 확장하거나, 리소스 여유 시 병렬 처리를 강화하는 '동적 실행 스케일링' 지능 구현.
