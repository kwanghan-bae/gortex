# Session 0090: Multi-Model Strategy Selection

## 📅 Date
2025-12-22

## 🎯 Goal
- **Multi-Model Strategy Selection**: 에이전트 평판 등급과 작업 중요도에 따라 Gemini-Pro, Flash, Ollama 중 최적의 모델을 자동 할당하는 시스템 구축.

## 📝 Activities
### 1. Grade-based Model Mapping
- `core/llm/factory.py`: `get_model_for_grade` 메서드 추가.
    - `Diamond`: `gemini-2.0-flash`
    - `Gold`: `gemini-pro-latest`
    - `Silver`: `gemini-1.5-flash`
    - `Bronze`: `gemini-2.5-flash-lite`
    - `Default`: `ollama/llama3`

### 2. Intelligent Manager Routing
- `agents/manager.py`: 타겟 에이전트의 평판 등급을 확인하여 `assigned_model`을 결정하는 로직 구현.
- 과거 성과 데이터(`EfficiencyMonitor`)와 결합하여 특정 작업에 최적화된 '전문가 모델' 우선 할당 모드 탑재.

### 3. Achievement & Feedback Loop
- `utils/economy.py`: 에이전트 등급 승급 시 `GortexState`의 업적 리스트에 기록하고 실시간 로깅하는 기능 보강.

### 4. Verification
- `tests/test_model_selection.py`를 통해 등급별 모델 할당 정합성 및 매니저 노드의 모델 주입 프로세스 검증 완료.

## 📈 Outcomes
- **Cost Efficiency**: 모든 작업에 고비용 모델을 쓰지 않고 실력에 따라 차등 배분하여 전체 운영 비용 최적화.
- **Incentive Structure**: 에이전트들이 고성능 모델(Pro)을 쓰기 위해 더 높은 품질의 결과물을 내놓도록 유도하는 생태계 완성.

## ⏭️ Next Steps
- **Session 0091**: Automated Bug Patching Loop.
- 시스템 로그에서 반복되는 에러 패턴을 감지하면, `Analyst`가 원인을 분석하고 `Coder`가 즉시 패치(Patch)를 생성하여 적용하는 '자율 수리 루프' 고도화.
