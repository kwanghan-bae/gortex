# Session 0085: Local LLM Performance Optimization

## 📅 Date
2025-12-22

## 🎯 Goal
- **Local LLM Performance Optimization (Ollama Integration)**: 로컬 모델(Ollama)의 안정성을 높이고 클라우드 API 할당량 소진 시 자동으로 전환되는 하이브리드 백엔드 구축.

## 📝 Activities
### 1. Hybrid Backend Implementation
- `core/llm/factory.py`에 `HybridBackend` 클래스 추가.
- Gemini 호출 실패(429 Quota 등) 감지 시 즉시 로컬 Ollama 모델로 폴백하는 로직 구현.
- `get_default_backend`의 기본값을 `hybrid`로 변경하여 시스템 탄력성 강화.

### 2. JSON Healing & Extraction
- `utils/tools.py`에 `repair_and_load_json` 함수 구현. 
- 로컬 모델의 특성상 발생하는 설명 문구 삽입, 괄호 누락, 홑따옴표 사용 등의 오류를 자동으로 교정.
- `OllamaBackend`에서 JSON 요청 시 이 기능을 자동으로 활용하도록 연동.

### 3. Verification
- `tests/test_hybrid_llm.py`를 통해 강제 에러 상황에서의 폴백 및 비정형 JSON 복구 성공 확인.

## 📈 Outcomes
- `core/llm/factory.py`: 스마트 폴백 지능 탑재.
- `core/llm/ollama_client.py`: 로컬 모델 응답 안정성 비약적 향상.
- `utils/tools.py`: 범용 JSON 복구 유틸리티 확보.

## ⏭️ Next Steps
- **Session 0086**: Dynamic Context Pruning.
- 대화가 길어질 때 토큰 비용을 절감하고 로컬 모델의 인지 범위를 확보하기 위해, 중요하지 않은 메시지를 지능적으로 가지치기하거나 요약하는 동적 컨텍스트 관리 시스템 구축.
