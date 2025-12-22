# Session 0108: Predictive Performance Guardrails

## 📅 Date
2025-12-23

## 🎯 Goal
- **Predictive Performance Guardrails**: 과거 데이터를 기반으로 작업 리소스 소모를 예측하고, 실행 전 임계치 초과 여부를 감지하여 시스템을 보호하는 선제적 방어 체계 구축.

## 📝 Activities
### 1. Resource Usage Prediction Engine
- `utils/efficiency_monitor.py`: `predict_resource_usage` 구현. 작업 성공 이력을 에이전트별로 집계하여 평균 토큰 및 실행 시간 예측 데이터 제공.

### 2. Planner Integration & Alerting
- `agents/planner.py`: 계획 수립 직후 전체 스텝의 누적 리소스 소모량을 산출.
- 일일 예산의 20%를 초과하는 고비용 작업 감지 시 "Resource Alert"를 발생시키고 사용자에게 경고 메시지 출력.

### 3. Dashboard Visualization Upgrade
- `ui/dashboard.py`: 사이드바의 `USAGE STATS` 패널 하단에 `PREDICTION` 섹션 신설.
- **예상 비용(Exp. Cost)** 및 **예상 소요 시간(Est. Time)**을 실시간 렌더링하여 작업 투명성 강화.

### 4. Integration Bridge
- `main.py`: 노드 출력물에서 `predicted_usage` 데이터를 가로채어 대시보드와 엔진 간의 데이터 전송 파이프라인 연동.

### 5. Verification
- `tests/test_performance_prediction.py`: 과거 이력을 통한 평균값 도출 및 플래너의 임계치 기반 경고 로직 정합성 검증 완료.

## 📈 Outcomes
- **Operational Foresight**: 작업을 시작하기 전 리스크를 인지함으로써 API 할당량 급소진이나 예기치 못한 작업 중단 예방.
- **Resource Consciousness**: 시스템 스스로가 '비싼 작업'을 인지하고 사용자에게 대안을 제안할 수 있는 기초 지능 확보.

## ⏭️ Next Steps
- **Session 0109**: Real-time System Energy Visualizer.
- 대시보드 중앙 상단에 시스템의 현재 에너지 상태와 충전 속도를 그래픽(Progress Bar)으로 보여주는 전용 패널을 추가하여 '살아있는 시스템'의 느낌 강화.
