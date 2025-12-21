# 📝 Gortex Release Notes & Work Log

> 💡 **Versioning Policy**: 메이저 버전(v1.x, v2.x ...)이 변경될 때마다 이전 기록은 `docs/archive/`로 이동하며, 메인 릴리즈 노트는 항상 최신 상태를 유지합니다.

## 🚀 Backlog (Pending Tasks)
- [x] **Intelligence**: 다중 에이전트 합의(토론) 프로토콜(Multi-Agent Consensus Protocol) 구현
- [x] **Intelligence**: 에이전트 간의 관점 차이를 조율하는 합의 도출(Synthesis) 알고리즘 고도화
- [x] **Interface**: 에이전트 간의 가상 토론 과정을 시각화하는 'Debate Monitor' 웹 UI 구축
- [x] **Intelligence**: 합의 결과의 유효성을 사후 평가하여 페르소나별 가중치를 동적으로 조절하는 'Consensus Learner' 도입
- [x] **Intelligence**: 외부 트렌드 및 기술 뉴스를 주기적으로 요약하여 'Synaptic Knowledge Base'로 통합하는 로직 구축
- [x] **Infrastructure**: 축적된 지식 중 유효하지 않거나 중복된 정보를 정리하는 'Knowledge GC' 노드 추가
- [x] **Intelligence**: 특정 라이브러리의 최신 API 문서를 실시간 학습하여 적용하는 'Live Documentation Learning' 구현
- [ ] **Intelligence**: 테스트 실패 로그를 분석하여 근본 원인을 추론하고 '실패 방지 규칙'을 자동 생성하는 'Reflective Debugging' 노드 추가

---

## ✅ Completed (Recent Milestones)

> 📦 **v1.x 대의 초기 개발 기록은 [release_note_v1.md](./archive/release_note_v1.md)에서 확인하실 수 있습니다.**

### v2.3.6 (Live Documentation Learning)
- [x] `agents/researcher.py`: 특정 라이브러리의 공식 문서를 타겟팅하여 핵심 API 시그니처를 지식화하는 `fetch_live_docs` 고도화
- [x] `agents/planner.py`: 신규 기술 도입 시 사전 문서 학습 단계를 의무화하는 'Docs-First Planning' 지침 보강
- [x] `utils/vector_store.py`: "LiveDocs" 출처의 실시간 지식을 장기 기억 저장소에 통합하여 에이전트 간 공유

### v2.3.5 (Knowledge Base Optimization)
- [x] `utils/vector_store.py`: 지식 활용도 측정을 위한 `usage_count` 기반 가치 평가 시스템 구축
- [x] `agents/analyst.py`: 중복 및 노후화된 지식을 자동으로 선별하고 제거하는 `Knowledge GC` 엔진 구현
- [x] `main.py`: 시스템 부팅 및 에이전트 분석 단계에 자동 최적화 파이프라인 통합

### v2.3.4 (Synaptic Knowledge Base Integration)
- [x] `agents/trend_scout.py`: 발견된 외부 기술 트렌드를 `LongTermMemory`에 자동 각인하는 지식 습득 파이프라인 구축
- [x] `agents/manager.py`: 최신 기술 트렌드 지식을 추론 과정에 우선적으로 반영하는 'Trend-Aware Reasoning' 구현
- [x] `utils/vector_store.py`: 지식의 출처(Source)와 유형(Type) 메타데이터를 통합 관리하여 정보 신뢰도 향상

### v2.3.3 (Consensus Performance Learner)
- [x] `core/state.py`: 합의안과 그 실행 성과(Performance)를 기록하는 `consensus_history` 구조 도입
- [x] `agents/analyst.py`: 과거 합의 결과의 효율성 점수를 추적하여 성공/실패 패턴을 스스로 학습하는 메커니즘 구현
- [x] `core/evolutionary_memory.py`: 학습된 합의 교훈을 영구 규칙(Rules)으로 승격시켜 향후 의사결정에 자동 반영

### v2.3.2 (Debate Monitor Visualization)
- [x] `ui/dashboard.py`: 상반된 페르소나의 의견을 대조하여 보여주는 'Debate Monitor' 위젯 구현
- [x] `main.py`: 실시간 토론 데이터를 터미널 및 웹 대시보드로 스트리밍하는 파이프라인 연동
- [x] `ui/dashboard.py`: 토론 모드 시 시각적 집중도를 높이기 위한 메인 패널 동적 레이아웃 전환 로직 추가

### v2.3.1 (Enhanced Consensus Synthesis)
- [x] `core/state.py`: 토론 데이터 전용 보관을 위한 `debate_context` 필드 도입
- [x] `agents/swarm.py`: 시나리오 원본 리포트와 메타데이터를 Analyst에게 무손실 전달하도록 개선
- [x] `agents/analyst.py`: 구조화된 시나리오 데이터를 바탕으로 정밀 트레이드오프 분석 및 실행 계획 수립 로직 고도화

### v2.3.0 (Multi-Agent Consensus Protocol)
- [x] `agents/swarm.py`: 상반된 관점(Innovation vs Stability)을 가진 페르소나 기반 시뮬레이션 로직 구현
- [x] `agents/analyst.py`: 토론 결과에서 트레이드오프를 분석하고 최종 합의안을 도출하는 `synthesize_consensus` 엔진 구축
- [x] `agents/manager.py`: 위험도 및 시스템 복잡도에 따른 지능형 '토론 모드' 활성화 워크플로우 안착
- [x] `docs/TECHNICAL_SPEC.md`: 합의 프로토콜을 위한 데이터 스키마 및 페르소나 정의 명문화

### v2.2.19 (Code Complexity Heatmap)
- [x] `agents/analyst.py`: 프로젝트 전체의 코드 복잡도를 스캔하여 점수화하는 `scan_project_complexity` 구현
- [x] `ui/dashboard.py`: 사이드바에 기술 부채(Technical Debt) 상위 파일을 시각화하는 패널 추가
- [x] `main.py`: `/scan_debt` 명령어로 수동 복잡도 분석 및 UI 업데이트 트리거 기능 추가

### v2.2.18 (Natural Language Macro)
- [x] `core/evolutionary_memory.py`: 매크로(Skill) 저장(`save_macro`) 및 조회(`get_macros`) 기능 구현
- [x] `agents/manager.py`: 사용자가 정의한 매크로를 학습하거나 실행하도록 지시하는 시스템 프롬프트 로직 추가

### v2.2.17 (Automated Test Generation)
- [x] `agents/planner.py`: 코드 수정 시 반드시 단위 테스트(`tests/test_*.py`) 작성 단계를 포함하도록 계획 수립 로직 강화
- [x] `agents/coder.py`: `unittest` 기반의 테스트 코드 작성 가이드라인을 시스템 프롬프트에 추가하여 품질 표준화

### v2.2.16 (Active Refactoring Proposal)
- [x] `agents/manager.py`: Tech Radar의 `adoption_candidates`를 확인하고 리팩토링 제안을 시스템 프롬프트에 자동 주입하는 로직 구현
- [x] `agents/manager.py`: `tech_radar.json` 파일 읽기 및 예외 처리를 위한 `json`, `os` 임포트 추가

### v2.2.15 (Tech Radar Auto-Adoption)
- [x] `agents/trend_scout.py`: 발견된 신기술이 프로젝트에 적용 가능한지 분석하는 `analyze_adoption_opportunity` 구현
- [x] `tech_radar.json`: 기술 도입 후보(`adoption_candidates`)를 영구 기록하도록 데이터 구조 확장

### v2.2.14 (Reputation-Based Model Allocation)
- [x] `core/state.py`: 에이전트에게 할당된 모델 ID를 저장하는 `assigned_model` 필드 추가
- [x] `agents/manager.py`: 에이전트 평판(Level)과 에너지 상태를 기반으로 모델(Flash vs Pro)을 차등 지급하는 로직 구현
- [x] `agents/coder.py`: Manager로부터 할당받은 `assigned_model`을 사용하여 작업을 수행하도록 업데이트

### v2.2.13 (Proactive Optimization Loop)
- [x] `core/state.py`: 효율성 이력을 추적하는 `efficiency_history` 필드 추가
- [x] `agents/manager.py`: 지속적인 저효율 발생 시 `optimizer`로 강제 라우팅하는 자가 치유(Self-Healing) 로직 구현
- [x] `agents/optimizer.py`: 저효율 원인을 진단하고 개선 작업을 제안하는 `diagnose_efficiency` 컨텍스트 분석 로직 추가

### v2.2.12 (Real-time Efficiency Visualization)
- [x] `ui/dashboard.py`: 사이드바에 현재 에너지(%)와 효율성 점수를 시각적으로 표시하는 위젯 추가 (Color-coded)
- [x] `main.py`: 메인 루프에서 매 턴마다 갱신된 에너지/효율성 정보를 UI 및 웹 대시보드로 실시간 전송하도록 파이프라인 확장

### v2.2.11 (Advanced Efficiency Integration)
- [x] `agents/swarm.py`: 병렬 작업 결과 취합 시 효율성 점수를 반영하여 최적의 안(Winner) 선정
- [x] `agents/manager.py`: 최근 효율성(`last_efficiency`)이 낮을 경우 상세 계획 수립을 지시하는 동적 프롬프트 적용

### v2.2.10 (Efficiency Scoring & Self-Optimization)
- [x] `agents/analyst.py`: 비용(토큰, 레이턴시, 에너지) 대비 성과를 측정하는 `calculate_efficiency_score` 메서드 구현
- [x] `core/evolutionary_memory.py`: 높은 효율성 점수를 기록한 작업 패턴을 영구 규칙으로 승격시키는 `promote_efficient_pattern` 로직 추가

### v2.2.9 (Energy-Aware Tasking & Work-Life Balance)
- [x] `core/state.py`: 에이전트의 가상 에너지 상태를 나타내는 `agent_energy` 필드 추가 (0~100)
- [x] `agents/manager.py`: 에너지 수준이 낮거나 API 호출이 빈번할 경우 자동으로 경량 모델(`flash-lite`)로 전환하는 지능형 스케줄링 구현
- [x] `main.py`: 에이전트의 작업 결과에 따라 에너지 소모가 세션 간 지속되도록 상태 업데이트 로직 강화
- [x] `agents/manager.py`: 에너지가 부족할 경우 복잡한 도구 호출을 자제하고 단순한 계획을 수립하도록 시스템 프롬프트 동적 주입

### v2.2.8 (Spatial Reasoning SDK & WebXR Foundation)
- [x] `ui/three_js_bridge.py`: VR/AR 기기와의 상호작용을 위한 공간 메타데이터(Glow, Haptic, Scale) 생성 로직 추가
- [x] `ui/web_server.py`: WebXR 기기를 식별하고 전용 고주파 스트리밍을 지원하는 멀티 기기 WebSocket 관리 시스템 구축
- [x] `ui/three_js_bridge.py`: 사고 트리를 3D 공간에 신경망 구조로 배치하는 시각화 알고리즘 고도화
- [x] `ui/web_server.py`: 기기별 맞춤형 데이터 브로드캐스팅(XR 전용 모드 등) 인터페이스 안착

### v2.1.0 ~ v2.2.7 요약
- [x] **v2.2.7**: AST 분석 기반의 3D Call Graph 시각화 엔진 구축
- [x] **v2.2.6**: 파이썬 코드 자원 효율성(Complexity) 정적 분석기 도입
- [x] **v2.2.0**: 실시간 보안 취약점 스캔(Shielded Generation) 엔진 안착
- [x] **v2.1.0**: 과거 오류 해결 패턴 기반의 자가 수복 메모리(Healing Memory) 구축
- [x] **v2.0.0**: 정밀 코드 편집을 위한 Virtual Cursor 및 Patch 도구 도입
