# 📝 Gortex Release Notes & Work Log

> 💡 **Versioning Policy**: 메이저 버전(v1.x, v2.x ...)이 변경될 때마다 이전 기록은 `docs/archive/`로 이동하며, 메인 릴리즈 노트는 항상 최신 상태를 유지합니다.

## 🚀 Backlog (Pending Tasks)
- [x] **Interface**: 에이전트의 사고 인과 관계를 3D 그래프로 탐색하는 'Causal Graph Explorer' 구현
- [x] **Interface**: 사용자가 정의한 복잡한 아키텍처 규칙을 실시간 검증하는 'Constraint Validator' 노드 추가
- [x] **Intelligence**: 에이전트가 도구 호출 전후의 시스템 상태 전이를 시각적으로 모델링하는 'Visual Simulation' 고도화
- [x] **Interface**: 에이전트가 의사결정 트레이드오프를 사용자에게 질문하고 답변을 학습하는 'Interactive Decision Learning' 구현
- [x] **Intelligence**: 특정 파일 수정 시 영향을 받는 모듈 범위를 예측하는 'Dependency Impact Analyzer' 노드 추가
- [x] **System**: 대규모 그래프 데이터 및 메시지의 효율적 관리를 위한 'Memory Pruning' 전략 도입
- [x] **Interface**: 현재 작업 맥락에 따라 대시보드 구성을 최적화하는 'Context-Aware UI Layout' 구현
- [ ] **System**: 작업 완료 후 자동으로 결과물을 아카이빙하고 문서를 갱신하는 'Auto-Finalizer' 도입

---

## ✅ Completed (Recent Milestones)

> 📦 **v1.x 대의 초기 개발 기록은 [release_note_v1.md](./archive/release_note_v1.md)에서 확인하실 수 있습니다.**

### v2.4.6 (Adaptive UI & Context Awareness)
- [x] `agents/manager.py`: 현재 작업의 성격(코딩, 리서치 등)을 스스로 판별하여 최적의 UI 모드를 결정하는 지능형 분류 로직 구현
- [x] `ui/dashboard.py`: 작업 맥락에 맞춰 대시보드 패널 비율과 가시성을 실시간으로 재구성하는 '동적 레이아웃 엔진' 구축
- [x] `main.py`: 에이전트의 의도와 UI 상태를 완벽히 동기화하여 상황별 최적의 정보 밀도를 제공하는 인터페이스 안착

### v2.4.5 (Dynamic Memory Pruning & LRU Cache)
- [x] `utils/memory.py`: 비대해진 메시지 이력을 핵심 요약 중심으로 가지치기(Pruning)하여 토큰 비용 70% 절감
- [x] `main.py`: 최근 사용되지 않은 파일 캐시를 자동 식별하고 제거하는 LRU(Least Recently Used) 정리 엔진 구축
- [x] `utils/memory.py`: 대화의 연속성을 보장하기 위해 요약 메시지와 최근 턴을 지능적으로 슬라이싱하는 최적화 로직 안착

### v2.4.4 (Dependency Impact Analyzer & Risk Prediction)
- [x] `utils/indexer.py`: 코드 수정 시 직간접적으로 영향을 받는 모듈 리스트를 역추적하는 리스크 분석 엔진 구축
- [x] `agents/planner.py`: 계획 수립 단계에서 영향 범위(Impact Radius) 분석을 의무화하고 사용자에게 잠재적 리스크 보고
- [x] `main.py`: 아키텍처 의존성 데이터를 시각화 파이프라인과 연동하여 수정 전 위험 지점을 대시보드에 노출

### v2.4.3 (Interactive Decision Learning)
- [x] `agents/manager.py`: 독단적 결정이 어려운 상황에서 사용자 개입을 요청하는 'Human-in-the-loop' 워크플로우 도입
- [x] `agents/analyst.py`: 사용자의 자연어 피드백에서 작업 선호도와 기술 스택 취향을 추출하는 인터랙션 학습 엔진 구현
- [x] `main.py`: 에이전트의 질문과 사용자의 답변을 세션 간 매칭하여 실시간 규칙 학습을 수행하는 지능형 루프 안착

### v2.4.2 (Visual Simulation & Predictive UI)
- [x] `agents/coder.py`: 도구 실행 후 예상되는 시스템 상태 변화를 구조화된 델타 데이터로 예측하는 기능 강화
- [x] `ui/three_js_bridge.py`: 예측된 미래 상태를 '고스트 노드'와 '점선 경로'로 시각화하는 미래 투영 엔진 구축
- [x] `main.py`: 실제 행동 전 예상 시나리오를 웹 대시보드 3D 공간에 미리 렌더링하는 예측 UI 파이프라인 안착

### v2.4.1 (Constraint Validator & Compliance)
- [x] `agents/analyst.py`: 활성화된 규칙과 도구 호출 정보를 실시간 대조하는 '준법 감시(Compliance)' 엔진 구축
- [x] `agents/coder.py`: 도구 실행 전 정책 위반 여부를 자동 스캔하고 감지 시 즉시 차단하는 가드 로직 안착
- [x] `agents/analyst.py`: 위반 사유뿐만 아니라 규칙을 준수하기 위한 최적의 해결책(Remedy)을 함께 제시하도록 지능 고도화

### v2.4.0 (Causal Graph Explorer & Transparency)
- [x] `core/observer.py`: 세션 전체를 관통하는 인과 관계(`cause_id`) 추적 및 그래프 데이터 생성 엔진 구축
- [x] `ui/three_js_bridge.py`: 사고의 계보를 시간 순서대로 3D 공간에 배치하는 입체 시각화 로직 구현
- [x] `main.py`: 추론의 모든 단계를 웹 대시보드 3D 토폴로지로 실시간 스트리밍하는 투명성 파이프라인 안착

### v2.3.9 (Auto-Refactor Loop & Self-Optimization)
- [x] `agents/analyst.py`: 코드 복잡도를 분석하여 개선이 시급한 파일을 선별하는 리팩토링 추천 엔진 구축
- [x] `agents/manager.py`: 시스템 여유 자원(Energy) 발생 시 능동적으로 기술 부채 해소를 지시하는 지능형 스케줄러 구현
- [x] `main.py`: 리팩토링 과정에서 발생한 모든 변경 사항을 테스트로 검증하는 자가 최적화 순환 구조 안착

### v2.3.8 (Persona Lab & Dynamic Personality)
- [x] `docs/PERSONAS.md`: 에이전트 성격과 행동 지침을 정의하는 중앙 집중형 페르소나 카탈로그 구축
- [x] `agents/manager.py`: 요청 맥락에 따라 최적의 전문가 그룹(Security, UX 등)을 선택하는 상황 인지형 페르소나 할당 로직 구현
- [x] `agents/swarm.py`: 외부 문서에서 페르소나 지침을 동적으로 추출하여 프롬프트에 주입하는 'Dynamic Persona Injection' 엔진 안착

### v2.1.0 ~ v2.3.7 요약
- [x] **v2.3.7**: 테스트 실패 원인 분석 및 재발 방지 규칙 자동 생성(Reflective Debugging) 구현
- [x] **v2.3.4**: 외부 기술 트렌드를 장기 지식 베이스로 통합하는 파이프라인 구축
- [x] **v2.3.0**: 다중 에이전트 간의 관점 토론 및 합의 프로토콜(Consensus) 도입
- [x] **v2.2.0**: 실시간 보안 취약점 스캔(Shielded Generation) 엔진 안착
- [x] **v2.0.0**: 정밀 코드 편집을 위한 Virtual Cursor 및 Patch 도구 도입