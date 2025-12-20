# 📝 Gortex Release Notes & Work Log

## 🚀 Backlog (To-Do)
- [ ] **Evolution**: Analyst 에이전트의 규칙 추출 성능 고도화
- [ ] **Polishing**: 대시보드 애니메이션 및 레이아웃 최적화

## ✅ Completed
### v1.1.2 (Portable Distribution)
- [x] `setup.sh`: 가상환경 자동 생성 및 `requirements.txt` 기반 패키지 설치 로직 강화
- [x] `run.sh`: 가상환경 자동 활성화 및 실행 실패 시 가이드 제공 래퍼 구현
- [x] `scripts/install_globally.sh`: 어디서든 `gortex` 명령어로 실행 가능하게 하는 글로벌 설치 스크립트 구현
- [x] `SPEC.md`: 개인 사용자용 포터블 배포 사양 반영 (Redis/Docker 필수 해제)

### v1.1.1 (Self-Cognition & Polishing)
- [x] `agents/optimizer.py`: 시스템 로그(`trace.jsonl`) 분석을 통한 병목 및 에러 패턴 감지 로직 구현
- [x] `ui/dashboard.py`: 에이전트 활동 시 Spinner(Dots) 애니메이션 추가로 시각적 피드백 강화
- [x] `core/graph.py`: `optimizer` 노드 추가 및 워크플로우 통합
- [x] `tests/test_optimizer.py`: 로그 분석 기능 단위 테스트 통과

### v1.1.0 (Refinement & Optimization)
- [x] `utils/token_counter.py`: 토큰 계산 및 비용 추정 유틸리티 구현
- [x] `utils/memory.py`: 12개 메시지 이상 시 작동하는 시냅스 압축(요약) 로직 구현
- [x] `core/graph.py`: `summarizer` 노드 추가 및 워크플로우 통합
- [x] `ui/dashboard.py`: 실시간 토큰 사용량 및 예상 비용 표시 기능 강화
- [x] `tests/test_token_counter.py`: 토큰 계산기 단위 테스트 통과

### v1.0.9 (Infrastructure & UI)
- [x] `main.py`: LangGraph 실행 엔진 및 SQLite 체크포인트 통합
- [x] `ui/dashboard.py`: Rich 기반의 실시간 2분할(Chat/Status) 대시보드 구현
- [x] `core/observer.py`: 구조화된 이벤트 로깅(JSONL) 및 관측 시스템 구현
- [x] `ui/dashboard_theme.py`: KORTEX 스타일 가이드 반영 테마 정의

### v1.0.8 (Agents: TrendScout & Graph)
- [x] `agents/trend_scout.py`: 부팅 시 신규 모델 및 기술 트렌드 스캔 로직 구현
- [x] `core/graph.py`: LangGraph를 활용한 전체 에이전트 워크플로우 통합
- [x] `tests/test_trend_scout.py`: 트렌드 스캔 및 분석 테스트 통과

### v1.0.7 (Agents: Analyst & Evolution)
- [x] `agents/analyst.py`: 데이터 분석(Pandas) 및 피드백 분석 모드 구현
- [x] `core/evolutionary_memory.py`: `experience.json` 기반 자가 진화 메모리 관리 구현
- [x] `tests/test_analyst.py`: 데이터 분석 및 피드백 학습 테스트 통과

### v1.0.6 (Agents: Researcher & Cache)
- [x] `agents/researcher.py`: Playwright 기반 웹 스크래핑 및 요약 로직 구현
- [x] `utils/cache.py`: Redis 싱글톤 캐시 매니저 구현 (폴백 포함)
- [x] `tests/test_researcher.py`, `tests/test_cache.py`: 단위 테스트 통과

### v1.0.5 (Agents: Coder)
- [x] `agents/coder.py`: Planner 계획 실행 및 CoVe(검증 후 수정) 루프 구현
- [x] `tests/test_coder.py`: 30회 루프 제한 및 도구 호출 로직 테스트 통과

### v1.0.4 (Agents: Planner)
- [x] `agents/planner.py`: 목표 분해 및 Atomic Step 계획 수립 로직 구현
- [x] `tests/test_planner.py`: 계획 생성 및 JSON 파싱 테스트 통과
- [x] `utils/tools.py`: `list_files`, `read_file` 도구 추가

### v1.0.3 (Agents: Manager)
- [x] `agents/manager.py`: 의도 분석 및 조건부 라우팅 로직 구현
- [x] `tests/test_manager.py`: 라우팅 및 제약 조건 주입 테스트 통과

### v1.0.2 (State & Tools)
- [x] `core/state.py`: GortexState TypedDict 정의
- [x] `utils/tools.py`: Atomic Write & Secure Shell 구현
- [x] `tests/test_tools.py`: 단위 테스트 통과

### v1.0.1 (Core Auth)
- [x] `core/auth.py`: 듀얼 키 로테이션 및 Anti-bot Jitter 구현
- [x] `tests/test_auth.py`: Mock 기반 단위 테스트 작성 및 통과

### v1.0.0 (Skeleton)
- [x] 프로젝트 디렉토리 구조 생성
- [x] `SPEC.md` (Master Specification) 작성
- [x] Git 초기화 및 `.gitignore` 설정
- [x] `README.md` 작성
