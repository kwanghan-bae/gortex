# 📝 Gortex Release Notes & Work Log

> 💡 **Versioning Policy**: 메이저 버전(v1.x, v2.x ...)이 변경될 때마다 이전 기록은 `docs/archive/`로 이동하며, 메인 릴리즈 노트는 항상 최신 상태를 유지합니다.

## 🚀 Backlog (Pending Tasks)
- [x] **System**: 핵심 설계 의사결정 및 컨텍스트 자동 고정 (Context Pinning) 구현
- [ ] **Infrastructure**: 변경된 파일만 식별하여 증분 테스트를 수행하는 'Selective Testing' 노드 추가
- [ ] **Interface**: 3D 그래프에서 영향 받는 노드들을 묶어 보여주는 'Dependency Clustering' 시각화

---

## ✅ Completed (Recent Milestones)

> 📦 **v1.x 대의 초기 개발 기록은 [release_note_v1.md](./archive/release_note_v1.md)에서 확인하실 수 있습니다.**

### v2.6.3 (Context Pinning & Immutable Decisions)
- [x] `core/state.py`: 삭제 및 요약 로직으로부터 격리되어 항상 보존되는 `pinned_messages` 레이어 도입
- [x] `agents/manager.py`: 중요한 판단 결과를 에이전트가 스스로 고정(Pin)할 수 있는 자율적 중요도 판정 기능 추가
- [x] `utils/memory.py`: 메시지 가지치기(Pruning) 시 고정된 컨텍스트를 최상단에 재주입하여 인지 일관성 확보

### v2.6.2 (Edge Case Rigor & Error Resilience)
- [x] `tests/`: Manager의 API 오류 대응 및 Analyst의 파싱 실패 등 예외 상황에 대한 단위 테스트 집중 보강
- [x] `agents/manager.py`: 외부 API 호출부를 안전한 에러 핸들링 블록으로 감싸 시스템 안정성 강화
- [x] `tests/test_planner.py`: 구조화된 영향 범위 분석(Impact Analysis) 데이터의 정합성 검증 로직 추가

### v2.6.1 (Strict QA & High-Rigor Pre-Commit)
- [x] `scripts/pre_commit.sh`: 린팅(Ruff) 및 테스트 존재 여부 강제 검사 기능을 포함한 고도화 (v1.3)
- [x] `docs/RULES.md`: 'Test-First' 원칙 및 테스트 없는 커밋 금지를 프로젝트 헌법으로 명문화
- [x] `docs/prompts/core_agents.yaml`: Planner/Coder에게 테스트 주도 개발(TDD) 사고방식을 강제하는 지침 보강

### v2.6.0 (Autonomous Pre-Commit & Self-Validation)
- [x] `agents/coder.py`: 작업 완료 선언 전 자가 검증을 의무화하고 실패 시 즉각 수정 루프를 도는 자율 검증 로직 구현
- [x] `docs/prompts/core_agents.yaml`: 검증 결과에 따른 행동 지침을 명문화하여 에이전트의 품질 책임 소재 강화
- [x] `main.py`: 에이전트의 내부 검증 로그를 사용자에게 실시간 노출하여 개발 과정의 신뢰성과 투명성 확보

### v2.5.9 (Global Dynamic Prompting)
- [x] `docs/prompts/core_agents.yaml`: 모든 에이전트의 지침을 통합 관리하는 외부 지능 저장소 완성
- [x] `agents/`: 모든 노드에서 하드코딩된 대규모 문자열을 제거하고 `PromptLoader`를 통한 동적 주입 체계 전면 도입
- [x] `utils/prompt_loader.py`: 변수 치환 및 템플릿 로딩 안정성을 강화하여 시스템 유연성 확보

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