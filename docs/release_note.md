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
- [x] **Intelligence**: 사용자의 다음 행동을 예측하여 선제적으로 제안하는 'Predictive Next-Action' 엔진 구축
- [x] **Intelligence**: 흩어진 지식들 간의 상관관계를 분석하여 지식 지도를 만드는 'Knowledge Relation Mapper' 도입
- [x] **Intelligence**: 사용자의 의도를 실시간으로 투영하여 워크플로우를 가이드하는 'User Intent Projection' 구축
- [x] **Infrastructure**: 지식 저장소를 프로젝트 단위로 분할 관리하는 'Memory Sharding' 도입
- [x] **System**: 대규모 그래프 데이터 및 메시지의 효율적 관리를 위한 'Memory Pruning' 전략 도입
- [x] **Interface**: 현재 작업 맥락에 따라 대시보드 구성을 최적화하는 'Context-Aware UI Layout' 구현
- [x] **System**: 작업 완료 후 자동으로 결과물을 아카이빙하고 문서를 갱신하는 'Auto-Finalizer' 도입
- [x] **Economy**: 에이전트 간 상호 평가를 통해 자원 할당 우선순위를 결정하는 'Peer Review Economy' 고도화
- [x] **System**: 지식 검색 성능을 비약적으로 높이는 'Vector Embedding Search'로의 전환
- [x] **Intelligence**: 에이전트의 모든 의미 있는 사고 과정을 스스로 요약하여 지식화하는 'Thought Memorization' 구현
- [ ] **Infrastructure**: 에이전트 프롬프트를 런타임에 수정 가능한 템플릿으로 분리하는 'Dynamic Prompting' 구축

---

## ✅ Completed (Recent Milestones)

> 📦 **v1.x 대의 초기 개발 기록은 [release_note_v1.md](./archive/release_note_v1.md)에서 확인하실 수 있습니다.**

### v2.5.7 (Memory Sharding & Performance)
- [x] `utils/vector_store.py`: 프로젝트 단위로 지식을 격리 저장하는 멀티 샤드(Namespace) 아키텍처 구현
- [x] `agents/manager.py`: 작업 디렉토리에 따라 전용 지식 샤드를 자동 탐색하는 지능형 컨텍스트 매칭 루틴 안착
- [x] `Infrastructure`: 지식 로딩 시 필요한 파티션만 메모리에 적재하여 시스템 리소스 효율성 극대화

### v2.5.6 (User Intent Projection & Roadmap)
- [x] `agents/manager.py`: 사용자의 자연어 입력 뒤에 숨겨진 장기 목표와 단계별 의도를 추출하는 '의도 투영' 지능 구현
- [x] `ui/three_js_bridge.py`: 투영된 의도를 시스템 수행 그래프 상단의 '목표 레이어'로 입체 시각화하는 로직 안착
- [x] `main.py`: 사용자의 비전과 에이전트의 활동을 실시간 동기화하여 시각적 로드맵을 제공하는 인터랙티브 UI 완성

### v2.5.5 (Knowledge Mapping & Meta-Cognition)
- [x] `agents/analyst.py`: 지식 간의 의미론적 유사성을 전수 분석하여 상관관계망(Links)을 형성하는 지식 지도 엔진 구현
- [x] `ui/three_js_bridge.py`: 구축된 지식 지도를 3D 공간에 연결선(Correlation)으로 시각화하여 지능의 입체적 구조 형상화

### v2.5.0 ~ v2.5.4 요약
- [x] **v2.5.4**: 현재 작업 맥락과 과거 패턴을 대조하여 사용자의 다음 행동을 실시간 예측하는 선점형 지능 구축
- [x] **v2.5.3**: 판단의 근거가 된 지식의 출처(Source)를 추적하여 UI 계보 데이터로 변환하는 로직 구현
- [x] **v2.5.2**: 우수한 성과를 낸 사고 과정을 추론 패턴으로 요약하여 장기 기억에 각인하는 엔진 구축
- [x] **v2.5.1**: Gemini Embedding API를 활용하여 지식 저장 시 자동으로 벡터화하는 엔진 도입
- [x] **v2.5.0**: 여러 텍스트를 한 번에 번역하는 배치 엔진을 구축하여 웹 대시보드 실시간 다국어 지원 실현

### v2.4.9 (Visual Impact Highlighting)
- [x] `ui/three_js_bridge.py`: 수정 시 영향을 받는 노드들을 붉은색으로 타오르게(Glow) 하는 시각적 리스크 표시 엔진 구현
- [x] `agents/planner.py`: 영향 범위 분석 데이터를 구조화된 JSON으로 반환하도록 고도화하여 시각화 엔진과 밀결합