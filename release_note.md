# 📝 Gortex Release Notes & Work Log

## 🚀 Backlog (To-Do)
- [ ] **Animation**: 에이전트 전환 시 더 부드러운 전환 효과 및 사운드 피드백(선택)
- [ ] **Context**: 토큰 소모 극대화를 위한 장기 세션에서의 중요 정보 압축 유지 전략

## ✅ Completed
### v1.3.3 (Evolution Stability & Patch Validation)
- [x] `core/evolutionary_memory.py`: 새로운 규칙 저장 시 기존 규칙과의 트리거 패턴 중복/충돌 감지 로직 구현
- [x] `agents/planner.py`: `Optimizer`가 제안한 시스템 최적화 패치의 타당성을 검토하고 수락/거절 이유를 명시하도록 프롬프트 고도화
- [x] `core/evolutionary_memory.py`: 충돌 감지 시 경고 로그 출력 및 안전한 규칙 관리 보장

### v1.3.2 (Self-Modification Realization & UI Polish)
- [x] `agents/optimizer.py`: API 할당량 초과 등에 대응하는 구체적인 '파일 기반 작업 지시문' 생성 로직 강화
- [x] `ui/dashboard.py`: 각 에이전트(Planner, Coder 등)마다 고유한 Spinner 스타일 적용으로 시각적 다양성 확보
- [x] `ui/dashboard.py`: 전체 UI 레이아웃 및 들여쓰기 정리 완료
- [x] `tests/test_optimizer.py`: 구조화된 데이터 반환 및 분석 로직 검증 완료

### v1.3.1 (Advanced Table Detection & Log Detailed View)
- [x] `utils/table_detector.py`: 단일 공백 구분 및 데이터 유실 가능성이 있는 행에 대한 복원 휴리스틱 로직 강화
- [x] `main.py`: `/log <index>` 명령어 추가로 특정 로그의 상세 페이로드(JSON) 확인 기능 구현
- [x] `main.py`: `/logs` 명령어 개선 (로그 인덱스 번호 표시 추가로 `/log`와 연동성 확보)
- [x] `ui/dashboard.py`: Rich Renderable 객체 처리 로직 안정화

### v1.3.0 (Self-Modification & Interactive Recovery)
- [x] `agents/manager.py`: `Optimizer`가 제안한 개선 태스크를 인지하고 `Planner`에게 우선순위로 전달하는 로직 구현
- [x] `main.py`: 사용자 중단(`Ctrl+C`) 후 재개 시 에이전트가 상황을 인식할 수 있도록 맥락 주입 로직 추가
- [x] `main.py`: `interrupted_last_time` 플래그를 통한 지능형 대화 상태 관리 구현
- [x] `main.py`: 코드 정리 및 인터랙티브 흐름 최적화

### v1.2.9 (User Interruption & Log Browsing)
- [x] `main.py`: 에이전트 실행 중 `Ctrl+C` 감지 시 세션 상태를 안전하게 보존하고 즉시 대기 모드로 복귀하는 로직 강화
- [x] `main.py`: `/logs` 명령어 추가로 최근 10개의 트레이스 로그를 테이블 형식으로 조회 가능
- [x] `ui/dashboard.py`: 채팅 패널에서 문자열 뿐만 아니라 Rich 객체(Table 등) 렌더링 지원 보강
- [x] `main.py`: 문법 오류 수정 및 명령어 처리기 안정화

### v1.2.8 (Table Refinement & Dynamic Thresholds)
- [x] `utils/table_detector.py`: 단일 공백 구분 테이블 및 불규칙한 공백이 포함된 행에 대한 감지 로직 고도화
- [x] `core/graph.py`: 총 토큰 수 추정치를 기반으로 한 동적 시냅스 압축(Summarizer) 임계치 도입 (5000 토큰 초과 시)
- [x] `core/graph.py`: 에이전트 노드 임포트 누락 수정 및 워크플로우 안정화

### v1.2.7 (User Interruption & Manual Summary)
- [x] `main.py`: 에이전트 실행 중 `Ctrl+C` 감지 시 전체 종료 대신 현재 작업만 안전하게 중단하도록 개선
- [x] `main.py`: `/summarize` 명령어 추가로 사용자가 원할 때 즉시 시냅스 압축(요약) 수행 가능
- [x] `main.py`: 명령어 처리 결과에 따른 흐름 제어 및 상태 유지 로직 최적화
- [x] `main.py`: 문법 오류 수정 및 비차단 입력 처리 안정화

### v1.2.6 (Few-shot Evolution & Markdown Tables)
- [x] `agents/analyst.py`: 규칙 추출 정확도 향상을 위해 시스템 프롬프트에 3개의 Few-shot 사례 추가
- [x] `utils/table_detector.py`: Markdown 스타일(`|` 구분자) 테이블 감지 및 파싱 로직 추가
- [x] `tests/test_ui.py`: Markdown 테이블 감지 단위 테스트 추가 및 통과

### v1.2.5 (Intelligent Optimization & UI Feedback)
- [x] `agents/optimizer.py`: 시스템 로그 분석 후 구조화된 'improvement_task'를 생성하도록 프롬프트 고도화
- [x] `agents/optimizer.py`: `Manager`가 인지할 수 있는 형식으로 개선안을 전달하여 자동 최적화 기반 마련
- [x] `ui/dashboard.py`: 사고 과정 완료 시 녹색 테두리와 'Thought complete' 문구로 시각적 마감 효과 추가
- [x] `main.py`: 에이전트 실행 완료 직후 UI 상태 동기화 로직 보강
- [x] `tests/test_optimizer.py`: 구조화된 데이터 반환에 맞춘 단위 테스트 업데이트 완료

### v1.2.4 (CLI Commands & Error Recovery)
- [x] `main.py`: 슬래시(/) 명령 처리기 구현 (`/clear`, `/history`, `/radar` 지원)
- [x] `agents/coder.py`: 도구 실행 실패 시 `stderr`를 분석하여 문법 교정, 패키지 설치 등을 수행하는 자가 치유 로직 강화
- [x] `main.py`: 명령어 입력 시 에이전트 그래프를 호출하지 않고 즉시 결과를 반환하도록 흐름 제어 최적화

### v1.2.3 (Interactive Interruption & UI Polish)
- [x] `main.py`: 비차단 방식의 사용자 입력(`get_user_input`) 도입 및 `Ctrl+C`를 통한 작업 중단 기반 마련
- [x] `ui/dashboard.py`: 도구 실행 시 사이드바에 실시간 `Progress` 바 표시 기능 추가
- [x] `ui/dashboard.py`: 에이전트 사고 과정(Thought) 업데이트 시 시각적 효과 및 에이전트별 색상 적용 완료
- [x] `ui/dashboard.py`: JSON, Table, Code 등 다양한 도구 결과물 시각화 통합 완료

### v1.2.2 (Intelligent File Caching)
- [x] `utils/tools.py`: 파일 내용의 MD5 해시를 계산하는 `get_file_hash` 유틸리티 추가
- [x] `agents/planner.py`: 현재 `file_cache` 상태를 인지하여 중복 읽기 단계를 생략하도록 프롬프트 개선
- [x] `agents/coder.py`: `read_file` 시 해시를 비교하여 변경되지 않은 경우 캐시된 내용을 사용하도록 로직 구현 (토큰 절약)
- [x] `agents/coder.py`: `write_file` 또는 `read_file` 성공 시 `file_cache`를 자동 업데이트하여 전역 상태 유지

### v1.2.1 (ASCII Table Visualization)
- [x] `utils/table_detector.py`: 텍스트 기반 테이블(CSV, 공백 구분 표) 감지 및 `Rich.Table` 변환 유틸리티 구현
- [x] `ui/dashboard.py`: 도구 실행 결과에서 테이블 형식을 자동 감지하여 시각화하도록 연동
- [x] `tests/test_ui.py`: 테이블 감지 로직 단위 테스트 추가 및 통과

### v1.2.0 (Enhanced Observation Visualization)
- [x] `ui/dashboard.py`: 도구 실행 결과(`Observation`) 중 JSON 데이터 감지 및 `Rich.JSON` 렌더링 기능 추가
- [x] `ui/dashboard.py`: SQL, Java 등 다양한 코드 패턴 감지 및 문법 하이라이팅 보강
- [x] `ui/dashboard.py`: 관측 데이터 표시 한도를 2000자로 확장 및 가독성 개선
- [x] `tests/test_ui.py`: UI 데이터 처리 및 로그 업데이트 단위 테스트 추가

### v1.1.9 (Evolution Refinement & Logic Tuning)
- [x] `agents/analyst.py`: 규칙 추출 시 구체적 적용 상황을 명시하는 `context` 필드 추가
- [x] `core/evolutionary_memory.py`: 동일 지침 중복 방지 및 `reinforcement_count` 기반 규칙 강화 로직 구현
- [x] `tests/test_analyst.py`: 규칙 강화 및 병합 기능 검증 테스트 추가 및 통과

### v1.1.8 (Advanced Theming & Log Analysis)
- [x] `ui/dashboard_theme.py`: 에이전트별 전용 색상 정의 (Manager, Planner, Coder 등)
- [x] `ui/dashboard.py`: 사이드바에 실시간 'Trace Logs' 패널 추가 및 최근 5개 이벤트 표시
- [x] `ui/dashboard.py`: 에이전트별 색상을 상태창 및 사고(Thought) 패널에 적용하여 인지력 향상
- [x] `main.py`: 실시간 로그 업데이트 연동 및 UI 데이터 흐름 최적화

### v1.1.7 (Observation Refinement & Resilience)
- [x] `ui/dashboard.py`: 도구 실행 결과(`Observation`) 패널에 `Rich.Syntax` 하이라이팅 적용 (코드 자동 감지)
- [x] `main.py`: 모든 API 키 소진 시(`Quota Exhausted`) 사용자 친화적인 경고 패널 출력 및 우아한 종료 구현
- [x] `ui/dashboard.py`: `Syntax` 및 `Text` 패널 레이아웃 최적화

### v1.1.6 (Context Stability & UI Feedback)
- [x] `utils/memory.py`: 시냅스 압축 시 '활성 제약 조건(Evolved Rules)'이 누락되지 않도록 요약 프롬프트 보강
- [x] `ui/dashboard.py`: 에이전트의 사고 과정(Thought) 업데이트 시 시각적 강조 효과(색상 변경) 추가
- [x] `main.py`: 노드 간 전환 시 UI 리셋 로직 연동으로 변화 인지력 향상

### v1.1.5 (Analyst Refinement & UI Polish)
- [x] `agents/analyst.py`: 자가 진화 규칙 추출 프롬프트 고도화 (부정 신호 감지 민감도 향상)
- [x] `ui/dashboard.py`: 도구 실행 결과(Observation)가 1000자 초과 시 자동 요약 표시 로직 추가
- [x] `core/auth.py`: `.env` 파일 로딩 경로 개선 및 API 키 인식 안정성 확보

### v1.1.4 (UI & Dashboard Refinement)
- [x] `ui/dashboard.py`: 실시간 에이전트 사고 과정(Thought)을 위한 전용 패널 추가
- [x] `ui/dashboard.py`: 역할별(User, AI, Tool, System) 메시지 시각적 구분 강화
- [x] `agents/`: Manager, Planner, Coder 에이전트가 사고 과정을 UI로 전달하도록 수정
- [x] `main.py`: 에이전트 이벤트 스트림에서 Thought 추출 및 UI 연동 로직 구현

### v1.1.3 (Analyst & Memory Refinement)
- [x] `agents/analyst.py`: 자가 진화 규칙 추출을 위한 프롬프트 고도화 (범용적 지침 추출 강화)
- [x] `core/evolutionary_memory.py`: 중복 규칙 감지 및 강화(Reinforcement) 로직 추가
- [x] `tests/test_analyst.py`: 규칙 중복 제거 및 병합 기능 테스트 추가 및 통과

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
