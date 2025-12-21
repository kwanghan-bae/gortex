# 📝 Gortex Release Notes & Work Log

> 💡 **Versioning Policy**: 메이저 버전(v1.x, v2.x ...)이 변경될 때마다 이전 기록은 `docs/archive/`로 이동하며, 메인 릴리즈 노트는 항상 최신 상태를 유지합니다.

## 🚀 Backlog (Pending Tasks)
- [x] **Interface**: 에이전트의 사고 인과 관계를 3D 그래프로 탐색하는 'Causal Graph Explorer' 구현
- [x] **Interface**: 사용자가 정의한 복잡한 아키텍처 규칙을 실시간 검증하는 'Constraint Validator' 노드 추가
- [x] **Intelligence**: 에이전트가 도구 호출 전후의 시스템 상태 전이를 시각적으로 모델링하는 'Visual Simulation' 고도화
- [x] **Interface**: 에이전트가 의사결정 트레이드오프를 사용자에게 질문하고 답변을 학습하는 'Interactive Decision Learning' 구현
- [x] **Intelligence**: 특정 파일 수정 시 영향을 받는 모듈 범위를 예측하는 'Dependency Impact Analyzer' 노드 추가
- [x] **Interface**: 파일 수정 영향 범위를 3D 그래프에 시각적으로 강조하는 'Visual Impact Highlighter' 구현
- [x] **Interface**: 모든 에이전트 출력과 문서를 실시간 다국어 번역하여 제공하는 'Omni-Translator' 구축
- [x] **Interface**: 현재 판단의 근거가 된 지식의 출처를 시각화하는 'Knowledge Lineage UI' 구축
- [x] **System**: 대규모 그래프 데이터 및 메시지의 효율적 관리를 위한 'Memory Pruning' 전략 도입
- [x] **Interface**: 현재 작업 맥락에 따라 대시보드 구성을 최적화하는 'Context-Aware UI Layout' 구현
- [x] **System**: 작업 완료 후 자동으로 결과물을 아카이빙하고 문서를 갱신하는 'Auto-Finalizer' 도입
- [x] **Economy**: 에이전트 간 상호 평가를 통해 자원 할당 우선순위를 결정하는 'Peer Review Economy' 고도화
- [x] **System**: 지식 검색 성능을 비약적으로 높이는 'Vector Embedding Search'로의 전환
- [x] **Intelligence**: 에이전트의 모든 의미 있는 사고 과정을 스스로 요약하여 지식화하는 'Thought Memorization' 구현
- [ ] **Intelligence**: 사용자의 다음 행동을 예측하여 선제적으로 제안하는 'Predictive Next-Action' 엔진 구축

---

## ✅ Completed (Recent Milestones)

> 📦 **v1.x 대의 초기 개발 기록은 [release_note_v1.md](./archive/release_note_v1.md)에서 확인하실 수 있습니다.**

### v2.5.3 (Knowledge Lineage & Reasoning Transparency)
- [x] `utils/vector_store.py`: 지식 소환 시 메타데이터와 유사도 점수를 함께 반환하도록 구조화 고도화
- [x] `agents/manager.py`: 판단의 근거가 된 지식의 출처(Source)를 추적하여 UI 계보 데이터로 변환하는 로직 구현
- [x] `ui/dashboard.py`: 실시간 추론 근거를 사이드바에 노출하여 에이전트의 지능적 '설명 가능성(Explainability)' 확보

### v2.5.2 (Autonomous Thought Memorization)
- [x] `agents/analyst.py`: 우수한 성과를 낸 사고 과정을 추론 패턴(Reasoning Pattern)으로 요약하여 장기 기억에 각인하는 엔진 구축
- [x] `main.py`: 에이전트 작업 완료 시 효율성 점수를 기반으로 가치 있는 생각을 자동 선별하여 저장하는 루프 안착

### v2.5.1 (Vectorized Long-term Memory)
- [x] `utils/vector_store.py`: Gemini Embedding API를 활용하여 지식 저장 시 자동으로 벡터화하는 엔진 도입
- [x] `LongTermMemory`: 단순 키워드 매칭을 코사인 유사도 기반의 의미론적 검색으로 교체하여 검색 정확도 혁신
- [x] `core/auth.py`: 외부 모듈에서 API 클라이언트에 안전하게 접근할 수 있는 `get_current_client` 메서드 추가

### v2.5.0 (Omni-Translator & Multi-language Support)
- [x] `utils/translator.py`: 여러 텍스트를 한 번에 번역하는 배치 엔진을 구축하여 웹 대시보드 실시간 다국어 지원 실현
- [x] `ui/web_server.py`: 웹 콘솔을 통해 사용자의 언어 선호도를 동적으로 수신하고 즉시 적용하는 인터랙티브 브리지 구축
- [x] `ui/dashboard.py`: 에이전트의 '생각'과 '진행 단계'를 전송 전 가상 번역하여 글로벌 협업 환경 조성

### v2.4.9 (Visual Impact Highlighting)
- [x] `ui/three_js_bridge.py`: 수정 시 영향을 받는 노드들을 붉은색으로 타오르게(Glow) 하는 시각적 리스크 표시 엔진 구현
- [x] `agents/planner.py`: 영향 범위 분석 데이터를 구조화된 JSON으로 반환하도록 고도화하여 시각화 엔진과 밀결합
- [x] `main.py`: 리팩토링 계획 수립 즉시 웹 대시보드의 3D 공간에 위험 지점을 하이라이트하는 실시간 경고 파이프라인 안착

### v2.4.7 ~ v2.4.8 요약
- [x] **v2.4.8**: 에이전트 성과에 따른 가상 화폐(Credits) 지급 및 고성능 모델 구매 경제 시스템 구현
- [x] **v2.4.7**: 세션 종료 시 활동 내역 요약 및 문서를 자동 갱신하는 Auto-Finalizer 엔진 안착

### v2.4.0 ~ v2.4.6 요약
- [x] **v2.4.6**: 작업 성격에 따라 대시보드 레이아웃과 위젯 비율을 자동으로 변경하는 Adaptive UI 구현
- [x] **v2.4.5**: 비대해진 메시지 이력을 핵심 요약 중심으로 가지치기(Pruning)하여 토큰 효율 극대화
- [x] **v2.4.4**: 코드 수정 시 직간접적으로 영향을 받는 모듈 리스트를 역추적하는 리스크 분석 엔진 구축
- [x] **v2.4.3**: 독단적 결정이 어려운 상황에서 사용자 개입을 요청하는 상호작용 학습 루프 도입
- [x] **v2.4.2**: 도구 실행 후 예상되는 시스템 상태 변화를 델타 데이터로 예측하는 기능 강화
- [x] **v2.4.1**: 활성화된 규칙과 도구 호출 정보를 실시간 대조하는 준법 감시(Compliance) 엔진 구축
- [x] **v2.4.0**: 세션 전체를 관통하는 인과 관계(cause_id) 추적 및 3D 그래프 시각화 엔진 구축
