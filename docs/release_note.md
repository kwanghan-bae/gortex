# 📝 Gortex Release Notes & Work Log

> 💡 **Versioning Policy**: 메이저 버전(v1.x, v2.x ...)이 변경될 때마다 이전 기록은 `docs/archive/`로 이동하며, 메인 릴리즈 노트는 항상 최신 상태를 유지합니다.

## 🚀 Backlog (Pending Tasks)
- [x] **Infrastructure**: 작업 로그와 체크포인트를 자동 압축/백업하는 'Autonomous Backup' 노드 추가
- [ ] **Interface**: 3D 그래프에서 영향 받는 노드들을 묶어 보여주는 'Dependency Clustering' 시각화 (v2.6.7 기반 고도화)
- [ ] **Infrastructure**: 에이전트 도구 메시지 i18n 전면 마이그레이션 완결

---

## ✅ Completed (Recent Milestones)

### v2.13.5 (2025-12-23)
- **Self-Evolution**: `Automated Agent Generation Loop` 완성. 시스템이 자신의 능력 공백을 분석하고, 새로운 전문가 에이전트를 스스로 설계 및 제조하여 영입하는 '지능 증식' 메커니즘 탑재.
- **Dynamic Loading**: 런타임 소스 코드 생성 및 즉시 활성화(Dynamic Spawning) 기술 안착.
- **Intelligence**: 에러 로그 및 미결 과제 기반의 '필요 역량 설계(Gap Analysis)' 지능 고도화.

### v2.13.4 (2025-12-23)
- **Interface**: `Interactive Dashboard Upgrade` 완료. `AgentRegistry` 연동을 통한 실시간 에이전트 목록 시각화 패널 도입.

### v2.13.2 (2025-12-23)
- **Migration**: 핵심 에이전트 3종(`Planner`, `Coder`, `Analyst`)의 v3.0 표준 마이그레이션 완료. 클래스 기반 구조로 전면 리팩토링 및 중앙 레지스트리 공식 등록.

### v2.11.9 (2025-12-22)
- **Self-Healing**: `Automated Bug Patching Loop` 구현. 시스템 에러 로그를 분석하여 원인을 특정하고, 코드 수정 후 무결성을 검증하는 자율 수리 프로세스 안착.

### v2.11.2 (2025-12-22)
- **Infrastructure**: `ReflectionAnalyst`에 자가 치유 문서 시스템(`Self-Healing Documentation`) 탑재. 코드와 문서 간의 불일치(Drift)를 AI가 감지하고 자동 치유 가능.
- **Onboarding**: `README.md` 전면 개편 및 `setup.sh` 안정성 강화 (PM/기획자 친화적인 원클릭 설치 경험 제공).
- **Maintenance**: 모델 호환성 확보를 위해 하드코딩된 모델명을 `gemini-2.0-flash`로 일괄 업데이트.

### v2.11.1 (2025-12-22)
- **Onboarding**: `README.md` 전면 개편 및 설치 스크립트 사용자 경험 개선.

### v2.11.0 (2025-12-22)
- **Agent**: Swarm 토론 엔진 고도화 및 Innovation/Stability 페르소나 분리. 라운드 기반 토론을 통한 합의 도출 로직 강화.

- **리팩토링 유실 복구**: `SelfHealingMemory`, `LongTermMemory` 하위 호환성 전수 복구.
- **TUI 시각화**: 사고 트리(Thought Tree) 터미널 렌더링 기능 추가.
- **안정성 강화**: 그래프 컴파일 로직 수정 및 런타임 에러(KeyError, TypeError) 해결.
- **전략 업데이트**: Web UI 개발 잠정 중단 및 TUI 우선 순위 설정.

### v2.8.4 (Hybrid Coder & Bounded Execution)
- **Agent**: `agents/coder.py`에 하이브리드 LLM 아키텍처를 적용하여 Gemini와 Ollama를 모두 지원하게 되었습니다.
- **Strategy**: 모델의 Native 기능 지원 여부에 따라 프롬프트 전략과 도구 호출 방식(Native vs Simulated)을 동적으로 전환합니다.
- **Resilience**: 정규식 기반 JSON 추출 로직을 도입하여 로컬 모델의 비정형 응답에 대한 파싱 신뢰도를 높였습니다.

### v2.8.3 (TUI Stability & Interface Rigor)
- **Quality**: `ui/terminal.py` 및 `ui/dashboard.py`의 테스트 커버리지를 80% 이상으로 확보하여 터미널 인터페이스의 신뢰성을 극대화했습니다.
- **Robustness**: UI 메시지 처리 루프 및 사이드바 갱신 로직에 방어적 코드를 도입하여 비정상적인 데이터 유입 시의 안정성을 확보했습니다.
- **Bug Fix**: `DashboardUI` 내의 누락된 로깅 모듈 정의 및 속성 초기화 오류를 전수 수정했습니다.

### v2.8.2 (Token Agnosticism & Phase 2 Prep)
- **Utility**: `utils/token_counter.py`를 개선하여 로컬 모델(Ollama) 사용 시 비용을 0으로 산정하고, 모델 독립적인 토큰 근사치 계산을 표준화했습니다.
- **Architecture**: `LLMBackend`에 기능 지원 여부(Structured Output, Function Calling) 확인 인터페이스를 추가하여 에이전트의 동적 전략 수립을 지원합니다.
- **Design**: `agents/coder.py`의 로컬 모델 전환을 위한 아키텍처 설계를 코드 레벨에 반영했습니다.

### v2.8.1 (Hybrid Memory Architecture)
- **Refactoring**: `utils/memory.py`의 Gemini 직접 의존성을 제거하고 `LLMFactory` 기반으로 전환하여, 로컬 모델(Ollama)로도 장기 기억 압축이 가능해졌습니다.
- **Compatibility**: 메시지 포맷(Tuple/Dict) 자동 변환 로직을 추가하여 기존 LangGraph 상태와의 호환성을 유지하면서 멀티 백엔드를 지원합니다.
- **Verification**: `tests/test_memory.py`를 리팩토링된 구조에 맞춰 갱신하고 100% 커버리지를 유지했습니다.

### v2.8.0 (Ollama Foundation & LLM Abstraction)
- **Architecture**: `core/llm/` 패키지를 신설하고 `LLMBackend` 추상 계층을 도입하여 멀티 모델(Gemini/Ollama) 하이브리드 운영의 기반을 닦았습니다.
- **Feature**: 로컬 Ollama 서버와 통신하는 `OllamaBackend` 및 기존 인증 모듈을 래핑한 `GeminiBackend`를 구현했습니다.
- **Flexibility**: `LLMFactory`를 통해 환경 변수 설정만으로 런타임에 AI 백엔드를 교체할 수 있는 유연성을 확보했습니다.

### v2.7.5 (Evolutionary Memory & Synaptic Optimization Rigor)
- **Quality**: `core/evolutionary_memory.py`의 규칙 강화, 충돌 감지, 매크로 및 GC 로직을 전수 검증하여 100% 커버리지를 달성했습니다.
- **Quality**: `utils/memory.py`의 맥락 압축 및 가지치기 로직의 예외 경로와 조기 반환 조건을 확보하여 100% 커버리지를 달성했습니다.
- **Refactoring**: `utils/memory.py` 내의 불필요한 중복 예외 처리 코드를 제거하여 구조를 단순화했습니다.
- **Verification**: `tests/test_evolutionary_memory.py` 신설 및 `tests/test_memory.py` 보강을 통해 시스템 기억 계층의 안정성을 극대화했습니다.

### v2.7.4 (Test Coverage Enforcement)
- **Quality**: `utils/tools.py`의 `list_files`, `execute_shell`, `archive_project_artifacts`, `compress_directory`가 경계 조건을 안전하게 처리하며 파일 및 압축 워크플로를 촘촘히 검증합니다.
- **Quality**: `tests/test_message_queue.py`에서 Redis가 없는 더미 세션과 `publish`/`push_task`/`pop_task` 경로를 Mock 기반으로 보호합니다.
- **Quality**: `tests/test_log_vectorizer.py`가 로그 인덱싱과 유사도 기반 검색을 테스트하여 trace 검색 근거를 뒷받침합니다.
- **Quality**: `tests/test_three_js_bridge.py`가 사고 트리를 3D 객체로 변환하면서 노드/엣지 계층과 채색 기준을 확인합니다.
- **Quality**: `tests/test_ui.py`, `tests/test_asset_manager.py`, `tests/test_table_detector.py`가 Dashboard 갱신, 에셋 로딩, 테이블 감지 로직을 단위/통합 수준에서 검증해 UI/유틸 핵심을 튼튼히 했습니다.
- **Quality**: `tests/test_translator.py`, `tests/test_engine.py`가 번역기(단일/배치)와 실행 루프(process_node_output, 힌트, 상태 업데이트) 경로를 감시해 언어/엔진 레이어를 강건하게 만들었습니다.
- **Quality**: `tests/test_auth.py`, `tests/test_observer.py`가 인증 계정 전환/콜 추적과 로그 인과 그래프/콜백 기록을 검증해 보안·감시 층을 강화했습니다.
- **Quality**: `tests/test_tools.py`, `tests/test_message_queue.py`가 파일/압축 작업, 해시 기반 무결성 검사와 Redis 메시징 흐름(게시/구독/작업 큐/더미 모드)을 검증해 시스템 툴킷의 안정성을 확보했습니다.
- **Quality**: `tests/test_notifier.py`, `tests/test_graph.py`가 알림 페이로드, 실패 로깅, 라우팅/그래프 컴파일의 분기 경로를 검증해 통신·워크플로 층을 강화했습니다.
- **Quality**: `tests/test_commands.py`, `tests/test_vector_store.py`가 슬래시 명령어 플로우, 내비게이션 피드백과 벡터 저장/소환(usage 증가, 유사도 필터, 예외 역행)을 테스트해 명령·기억 계층의 경계 조건을 확보했습니다.
- **Verification**: `PYTHONPATH=/Users/joel/Desktop/git coverage run -m pytest` → `coverage report`로 전체 80% 커버리지를 달성하고 다음 타깃(`core/evolutionary_memory.py`, `utils/memory.py`)을 설정했습니다.

### v2.7.2 (Core Modularization & High-Rigor Testing)
- [x] **Architecture**: 1,000라인의 `main.py`를 `engine`, `commands`, `terminal`로 완벽히 해체 및 기능별 전문화 (유실 로직 전수 복구)
- [x] **Refactoring**: `analyst.py`를 `reflection`, `organizer`, `base` 서브 모듈로 분산하여 지식 정리 및 아카이빙 로직 정교화
- [x] **Quality**: `Indexer`, `Translator`, `GortexEngine` 등에 대한 20개 이상의 정밀 테스트 케이스 신규 추가 (전체 55개 달성)
- [x] **Stability**: API 할당량 대응, 인과 관계 추적, 보안 감시 로직의 모듈 간 결합 무결성 재확보

### v2.7.1 (Autonomous Session Backup & Recovery)
- [x] `utils/tools.py`: 디렉토리 전체를 특정 패턴 제외하고 ZIP 패키징하는 고성능 압축 엔진 구축
- [x] `agents/analyst.py`: 세션 종료 시 모든 지식, 로그, 문서를 하나의 아카이브로 자동 백업하는 복원력 강화
- [x] **Integrity**: 파일 유실 사고에 대비한 코어 로직 재건 및 이스케이프 구문 오류 전면 수정을 통한 무결성 보장

### v2.7.0 (Dynamic Persona & Intellectual Diversity)
- [x] `docs/i18n/personas.json`: Standard, Innovation, Stability, Security, UX 등 전문화된 5종의 에이전트 성격 사전 구축
- [x] `agents/manager.py`: 요청 성격에 따라 최적의 전문가 페르소나를 자율 선택하여 할당하는 동적 라우팅 지능 구현
- [x] `utils/prompt_loader.py`: 할당된 페르소나 지침을 시스템 프롬프트에 실시간 합성하여 에이전트의 사고 톤을 변조하는 엔진 안착

### v2.6.10 (AI-Laziness Guard & Integrity Assurance)
- [x] **Defense**: `pre_commit.sh` 내에 AI 생략 기호(# ..., (중략) 등)를 자동 감지하여 커밋을 차단하는 고성능 스캐너 구축
- [x] **Testing**: 핵심 파일과 필수 메서드의 유실 여부를 실시간 검사하는 `test_integrity.py` 신설
- [x] **Policy**: `RULES.md`에 플레이스홀더 삽입 금지 조항을 명문화하여 에이전트의 무결성 책임 강화
- [x] **Recovery**: `swarm.py`, `analyst.py` 등 코드베이스 전체의 잔여 오염 지점 전수 복구 및 검증 완료

### v2.6.9 (Integrity Recovery & Message Migration)
- [x] **Critical Fix**: 코드 수정 도구 오용으로 발생한 소스 오염(중략 기호 삽입)을 전면 스캔하여 복구 및 무결성 재검증
- [x] `docs/i18n/`: Planner, Coder, Analyst 등 모든 핵심 에이전트의 응답 메시지를 다국어 사전 체계로 전면 마이그레이션 완료
- [x] `Infrastructure`: `i18n.t` 기반의 메시지 출력 방식을 표준화하여 시스템의 글로벌 서비스 기반 확보

### v2.6.7 ~ v2.6.8 요약
- [x] **v2.6.8**: 시스템 전역 다국어 지원(i18n) 엔진 및 데이터 인프라 구축
- [x] **v2.6.7**: 3D 의존성 그래프 노드 자율 군집화(Clustering) 및 시각화 시스템 구현

### v2.6.4 ~ v2.6.6 요약
- [x] `utils/tools.py`: 프로젝트 부산물들을 명명 규칙에 따라 안전하게 격리 보관하는 아카이빙 엔진 구축
- [x] `agents/analyst.py`: 세션 종료 시 작업 공간을 스캔하여 백업 및 임시 파일을 자동 정리하는 지능형 클리너 구현
- [x] `Infrastructure`: 누적되는 작업 로그와 버전을 프로젝트별로 구조화하여 장기적인 유지보수성 확보

### v2.6.5 (Multimodal Thought Visualization & Diagrams)
- [x] `agents/`: 사고 트리(`thought_tree`) 스키마에 `visual_payload` 필드를 추가하여 시각적 추론 기반 마련
- [x] `docs/prompts/`: Planner에게 복잡한 설계 시 Mermaid 다이어그램 작성을 강제하는 'Visual Reasoning' 규칙 도입
- [x] `ui/three_js_bridge.py`: 사고 노드와 다이어그램 코드를 결합하여 웹 대시보드로 실시간 전송하는 데이터 파이프라인 안착

### v2.6.4 (Selective Incremental Testing)
- [x] `utils/tools.py`: 캐시 해시 비교를 통해 현재 수정된 파일들만 기민하게 식별하는 엔진 구현
- [x] `scripts/pre_commit.sh`: 특정 파일과 연관된 테스트만 골라 실행하는 선택적 검증 모드(v1.4) 도입
- [x] `agents/coder.py`: 자율 검증 루프에 증분 테스트를 결합하여 개발 생산성 및 피드백 속도 획기적 개선

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