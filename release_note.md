# 📝 Gortex Release Notes & Work Log

## 🚀 Backlog (To-Do)
- [x] **Interface**: 대규모 로그 조회 시 페이징 처리 로직 추가
- [x] **System**: 비정상 종료 시 미처 저장되지 않은 인메모리 캐시 복구 전략 고도화
- [x] **Interface**: 대시보드 로그 위젯에 에이전트별 색상 필터링 추가
- [x] **Intelligence**: 자가 수정(Self-Correction) 패턴 분석 및 진화 규칙 자동 생성 로직 기초 설계
- [x] **Infrastructure**: 다중 사용자 세션 관리를 위한 스레드 분리 및 상태 격리 강화
- [x] **Infrastructure**: 세션 상태(Snapshot) 수동 익스포트 및 복구 도구 구현
- [x] **Interface**: `/import` 시 이전 세션의 '생각(Thought)' 로그도 복구하여 추론 일관성 유지
- [x] **Infrastructure**: API 키 할당량 소진 시 자동으로 다른 서비스(예: OpenAI, Anthropic)로 폴백하는 멀티 LLM 브리지 구축
- [x] **Interface**: 대시보드에 실시간 LLM 공급자 상태(Gemini/OpenAI) 및 잔여 할당량 시각화
- [x] **System**: 대규모 코드베이스 분석을 위한 'Synaptic Indexing' (AST 기반 코드 검색) 엔진 구축
- [x] **Intelligence**: 인덱싱된 코드 구조를 LLM 프롬프트에 동적으로 주입하여 '코드 맥락 인식' 능력 고도화
- [x] **Interface**: 코드 인덱스 검색 결과를 시각화하여 보여주는 `/search [symbol]` 명령어 구현
- [x] **Infrastructure**: `requirements.txt` 분석을 통해 누락된 의존성을 자동으로 설치하는 'Auto-Dependency' 노드 추가
- [x] **Interface**: 인덱싱된 프로젝트의 전체적인 관계도를 시각화하는 `/map` 명령어 구현
- [x] **Infrastructure**: `setup.sh`를 개선하여 Docker 환경 구성을 자동화하는 'Containerization' 지원
- [x] **Interface**: 현재 프로젝트를 ZIP 파일로 압축하여 다운로드 가능한 링크를 제공하는 `/bundle` 명령어 구현
- [x] **Infrastructure**: `TrendScout` 에이전트를 확장하여 새로운 파이썬 라이브러리나 기술 스택의 취약점을 점검하는 'Security Scout' 기능 추가
- [x] **Infrastructure**: GitHub API 연동을 통해 프로젝트를 원격 저장소에 자동으로 푸시하는 '/deploy' 명령어 구현
- [x] **Infrastructure**: 외부 API 연동(예: Slack, Discord)을 통해 작업 완료 시 알림을 보내는 'Notification' 시스템 구축
- [x] **Interface**: 터미널 UI를 넘어 브라우저에서 Gortex의 활동을 실시간 모니터링할 수 있는 'Web Dashboard' 프레임워크 구축
- [x] **Infrastructure**: 에이전트의 도구 호출 로그를 분석하여 비용과 지연 시간을 최적화하는 'Performance Profiler' 노드 구현
- [x] **Interface**: 사용자의 복잡한 요구사항을 시각적 다이어그램으로 변환하여 보여주는 'Architecture Sketcher' 기능 추가
- [x] **System**: 대규모 로그 데이터를 벡터화하여 유사한 오류 해결 사례를 검색하는 'Semantic Log Search' 엔진 추가
- [x] **Infrastructure**: 에이전트의 작업 성과를 리포트로 자동 요약하여 제공하는 'Executive Reporter' 기능 구현
- [x] **Infrastructure**: 다중 언어 지원을 위한 'Synaptic Translator' 노드 및 다국어 UI 프레임워크 구축
- [x] **Interface**: 웹 대시보드에 실시간 로그 스트리밍을 넘어서는 'Interactive Console' 기능 추가
- [x] **Infrastructure**: 외부 깃허브 이슈(Issues)나 PR을 분석하여 작업을 자동 할당하는 'GitHub Agent' 기능 구축
- [x] **System**: 에이전트가 코드를 작성하기 전 최신 오픈소스 라이브러리 및 API 문서를 검색하여 참조하는 'Live Documentation' 노드 추가
- [x] **Infrastructure**: 대시보드 UI 테마를 사용자의 취향에 맞게 동적으로 변경할 수 있는 'Theming Engine' 구축
- [x] **Intelligence**: 에이전트의 복합적인 사고 과정을 구조화하여 보여주는 'Thought Mindmap' 시각화 로직 구현
- [x] **Infrastructure**: 시스템 내부의 모든 전역 설정을 중앙에서 관리하는 'Dynamic Config Manager' 구축
- [x] **Infrastructure**: 에이전트의 작업 부하를 분산하기 위해 여러 LLM을 동시에 호출하는 'Agent Swarm' 프레임워크 기초 설계
- [x] **Infrastructure**: 병렬 작업 간의 데이터 충돌을 방지하고 상태를 안전하게 병합하는 'State Merger' 로직 고도화
- [x] **Intelligence**: 에이전트가 작업 중 발생한 감정적/논리적 교착 상태를 감지하여 스스로 재설정(Reset)하는 'Mental Reboot' 기능 구현
- [ ] **Interface**: 에이전트의 내부 사고 과정을 시각적으로 필터링하고 검색할 수 있는 'Thought Browser' UI 고도화

## ✅ Completed
### v1.9.3 (Mental Reboot & Stuck State Detection)
- [x] `agents/optimizer.py`: 동일한 도구 호출이 반복되는 '교착 상태(Stuck State)'를 실시간으로 감지하는 알고리즘 구현
- [x] `agents/optimizer.py`: 교착 상태 감지 시 즉시 'Mental Reboot'을 수행하여 에이전트의 사고를 초기화하고 새로운 방향성을 강제하는 워크플로우 안착
- [x] `agents/optimizer.py`: 성능 분석 리포트 프롬프트를 최적화하여 기존 테스트 케이스와의 호환성 및 분석 정밀도 향상
- [x] `tests/test_optimizer.py`: 새로운 자가 재부팅 로직을 반영하도록 단위 테스트 코드를 고도화하여 시스템 안정성 검증 완료

### v1.9.2 (Real-time Resource Monitoring)
- [x] `utils/resource_monitor.py`: `psutil`을 활용하여 시스템 및 Gortex 프로세스의 CPU, RAM 사용량을 정밀 측정하는 엔진 신설
- [x] `main.py`: 백그라운드 비동기 루프를 통해 실시간 리소스 통계를 주기적으로 수집하고 관리하는 인프라 구축
- [x] `ui/web_server.py`: 수집된 리소스 데이터를 웹 대시보드로 실시간 브로드캐스팅하여 시각적 모니터링 지원
- [x] `utils/resource_monitor.py`: 외부 라이브러리 부재 시에도 예외 처리를 통해 안정적인 시스템 실행 보장

### v1.9.1 (State Merger & Conflict Resolution)
- [x] `agents/swarm.py`: 병렬로 실행된 하위 작업들의 결과(`file_cache` 델타)를 메인 상태에 안전하게 통합하는 병합 로직 구현
- [x] `agents/swarm.py`: 동일 파일에 대한 서로 다른 변경 사항을 감지하고 사용자에게 경고하는 충돌 해결 전략 도입
- [x] `agents/swarm.py`: 각 병렬 작업의 리포트를 취합하여 하나의 응답 메시지로 구성하는 데이터 취합 시스템 강화
- [x] `agents/swarm.py`: JSON 형식의 하위 작업 결과 파싱 및 예외 처리를 통한 비동기 실행 안정성 확보

### v1.9.0 (Agent Swarm & Parallel Tasking Foundation)
- [x] `agents/manager.py`: 복잡한 요청을 여러 하위 작업으로 분리하고 `swarm` 노드로 라우팅하는 병렬 작업 감지 로직 구현
- [x] `agents/swarm.py`: `asyncio.gather`를 사용하여 여러 하위 작업을 동시에 실행하고 결과를 취합하는 오케스트레이션 노드 신설
- [x] `core/graph.py`: 시스템 워크플로우에 `swarm` 노드를 정식 등록하고 유연한 조건부 라우팅 구조 구축
- [x] `agents/manager.py`: 병렬 작업용 응답 스키마(`parallel_tasks`) 확장 및 동적 모델 선택 로직 연동

### v1.8.9 (Dynamic Config Manager & Global Settings)
- [x] `core/config.py`: 로그 레벨, 모델 선택, 임계치 등 전역 설정을 싱글톤으로 관리하는 `GortexConfig` 클래스 신설
- [x] `main.py`: 현재 시스템 설정을 실시간으로 조회하고 수정할 수 있는 `/config [key] [value]` 명령어 구현
- [x] `core/config.py`: 설정 변경 시 `gortex_config.json` 파일에 즉시 영속화하여 재부팅 후에도 설정 유지 지원
- [x] `main.py`: 동적 테마 엔진과 설정 매니저를 통합하여 중앙 집중식 시스템 제어 인터페이스 강화

### v1.8.8 (Thought Mindmap & Graph Visualization)
- [x] `ui/dashboard.py`: 선형적인 사고 트리를 노드와 엣지로 구성된 그래프 구조로 자동 변환하는 `_generate_thought_graph` 구현
- [x] `agents/manager.py` & `agents/planner.py`: 사고 노드에 우선순위(`priority`)와 확신도(`certainty`) 메타데이터를 포함하도록 스키마 확장
- [x] `ui/dashboard.py`: 변환된 마인드맵용 그래프 데이터를 웹 대시보드로 실시간 스트리밍하는 파이프라인 안착
- [x] `ui/dashboard.py`: 사고 과정의 논리적 연결 고리를 명시적으로 표현하여 에이전트의 판단 근거 가시성 극대화

### v1.8.7 (Dynamic Theming Engine & Visual Customization)
- [x] `ui/dashboard_theme.py`: Classic, Matrix, Cyberpunk, Monochrome 등 다양한 프리셋 테마를 지원하는 `ThemeManager` 클래스 신설
- [x] `main.py`: 실시간으로 UI 테마를 조회하고 변경할 수 있는 `/theme [name]` 명령어 구현
- [x] `main.py`: 테마 변경 시 `DashboardUI`의 콘솔 스타일을 즉시 동기화하여 시각적 즉각성 확보
- [x] `ui/dashboard_theme.py`: 에이전트별 전용 색상과 시스템 상태 색상을 테마별로 최적화하여 일관된 사용자 경험 제공

### v1.8.6 (Live Documentation & Real-time API Search)
- [x] `agents/researcher.py`: 특정 라이브러리의 공식 문서와 API 레퍼런스를 정밀하게 검색 및 추출하는 `fetch_api_docs` 구현
- [x] `agents/researcher.py`: 사용자 요청으로부터 문서 검색 필요성을 자동 감지하고 최적의 기술 쿼리를 생성하는 인텔리전스 강화
- [x] `agents/researcher.py`: 지능형 예외 처리 및 모델 스로틀링(Adaptive Throttling) 연동으로 시스템 안정성 확보
- [x] `agents/researcher.py`: 검색된 API 시그니처와 예제 코드를 요약하여 Coder의 맥락 인지 능력을 높이는 기반 마련

### v1.8.5 (GitHub Agent & PR Automation)
- [x] `utils/git_tool.py`: GitHub API(v3)를 연동하여 오픈된 이슈 목록 조회 및 Pull Request 자동 생성 기능 구현
- [x] `main.py`: 현재 브랜치의 변경 사항을 원격에 푸시하고 PR을 즉시 생성하는 `/pr [owner/repo] [title]` 명령어 추가
- [x] `utils/git_tool.py`: `GITHUB_TOKEN` 환경 변수를 통한 보안 인증 및 API 호출 헤더 최적화
- [x] `main.py`: 배포(`deploy`)와 PR 생성 워크플로우를 분리하여 더 세밀한 버전 관리 제어 지원

### v1.8.4 (Code Reviewer & Quality Scoring)
- [x] `agents/analyst.py`: 파이썬 코드를 Clean Code 및 PEP8 기준으로 정밀 분석하는 `review_code` 엔진 구현
- [x] `agents/analyst.py`: 스타일, 복잡도, 주석 적정성을 수치화(Score)하고 구체적인 리팩토링 팁을 생성하는 로직 추가
- [x] `agents/analyst.py`: 리뷰 결과 점수가 낮을 경우 자동으로 `planner`로 라우팅하여 자가 개선을 유도하는 워크플로우 통합
- [x] `agents/analyst.py`: 다국어 및 다양한 메시지 포맷(Tuple/Object)에 대한 예외 처리 및 분기 로직 강화

### v1.8.3 (Interactive Web Console & Bi-directional Sync)
- [x] `ui/web_server.py`: WebSocket을 통해 클라이언트로부터 사용자 입력을 수신하고 큐(`input_queue`)에 저장하는 기능 구현
- [x] `main.py`: 터미널 입력과 웹 입력 큐를 비동기적으로 동시 감시하여 먼저 발생한 입력을 처리하는 멀티 채널 입력 시스템 구축
- [x] `ui/web_server.py`: JSON 형식의 명령어를 파싱하여 `user_input` 타입의 메시지를 식별하고 처리하는 로직 추가
- [x] `main.py`: 웹 콘솔을 통해 원격지에서도 Gortex에게 직접 명령을 내리고 개입할 수 있는 양방향 통신 인프라 안착

### v1.8.2 (Synaptic Translator & Multi-language Support)
- [x] `utils/translator.py`: 입력 텍스트의 언어를 감지하고 자연스러운 한국어/목표 언어 번역을 수행하는 지능형 번역 엔진 구축
- [x] `agents/manager.py`: 사용자의 입력 언어를 자동 감지하여 시스템의 처리 맥락(한국어 우선)과 응답 언어를 동적으로 선택하도록 통합
- [x] `utils/translator.py`: 기술 용어 보존 및 자연스러운 문체 변환을 위한 전문 번역 프롬프트 최적화
- [x] `agents/manager.py`: 다국어 환경에서도 일관된 추론 품질을 유지할 수 있도록 내부 번역 브리지 구조 설계

### v1.8.1 (Achievement Timeline Widget)
- [x] `ui/dashboard.py`: 세션의 주요 마일스톤을 시간순으로 기록하는 `achievements` 데이터 구조 및 관리 로직 추가
- [x] `main.py`: 에이전트의 작업 완료, 계획 수립, 파일 수정 등 성공적인 이벤트를 감지하여 성과 타임라인에 자동 등록
- [x] `ui/dashboard.py`: 등록된 성과 데이터를 웹 대시보드로 실시간 브로드캐스팅하여 시각적 피드백 강화
- [x] `ui/dashboard.py`: 성과 잠금 해제(Achievement Unlocked) 시 로그 기록 및 아이콘 기반 시각화 준비

### v1.8.0 (Executive Performance Reporter)
- [x] `agents/analyst.py`: 로그 데이터를 분석하여 성공률, 비용, 지연 시간, 주요 성과를 요약하는 `generate_performance_report` 구현
- [x] `main.py`: 분석된 성과를 마크다운 형식으로 출력하는 `/report` 명령어 추가
- [x] `main.py`: `/report --notify` 옵션을 통해 생성된 리포트를 Slack/Discord 외부 채널로 즉시 전송하는 기능 연동
- [x] `agents/analyst.py`: 임원 보고용(Executive Report) 스타일의 LLM 요약 프롬프트 최적화로 가독성 및 비즈니스 가치 강조

### v1.7.9 (Semantic Log Search & Case-Based Reasoning)
- [x] `utils/log_vectorizer.py`: `trace.jsonl` 로그 파일의 주요 이벤트를 인덱싱하고 키워드 기반 유사 사례를 검색하는 엔진 구현
- [x] `agents/manager.py`: 사용자 요청 처리 전 과거의 유사한 해결 사례를 검색하여 프롬프트에 참조(Reference) 맥락으로 자동 주입
- [x] `utils/log_vectorizer.py`: 에이전트명, 이벤트 타입, 페이로드 정보를 결합한 다차원 검색 인덱스 구조 설계
- [x] `agents/manager.py`: 사례 기반 추론(CBR) 기법을 도입하여 과거의 성공 패턴을 현재 작업에 능동적으로 재활용하도록 고도화

### v1.7.8 (Mental Sandbox & Pre-Action Simulation)
- [x] `agents/coder.py`: 도구 호출 전 예상 결과와 위험 요소를 분석하는 Mental Sandbox 규칙 및 지침 추가
- [x] `agents/coder.py`: 위험도가 높은 작업(데이터 유실 등) 감지 시 도구 실행을 스스로 중단하고 안전한 대안을 제시하도록 로직 보강
- [x] `agents/coder.py`: 응답 스키마에 `simulation` 필드를 추가하여 에이전트의 사전 시뮬레이션 결과를 명시적으로 기록
- [x] `agents/coder.py`: 사고 과정 트리와 시뮬레이션 결과를 연동하여 더 안전하고 정교한 개발 환경 구축

### v1.7.7 (Architecture Sketcher & Mermaid Integration)
- [x] `agents/planner.py`: 시스템 설계 시 Mermaid 형식의 다이어그램 코드를 생성하는 `diagram_code` 필드 및 지침 추가
- [x] `ui/dashboard.py`: 생성된 아키텍처 다이어그램 데이터를 수용하고 웹 대시보드로 실시간 스트리밍하는 인터페이스 확장
- [x] `main.py`: 에이전트 스트리밍 루프에서 다이어그램 코드를 추출하여 UI 및 웹 서버에 동기화하도록 통합
- [x] `agents/planner.py`: 설계 과정을 구조화된 트리와 시각적 도식화로 동시에 제공하여 아키텍처 가시성 극대화

### v1.7.6 (Reflective Validation & Self-Correction Loop)
- [x] `agents/coder.py`: 코드 수정(`write_file`) 직후 반드시 `execute_shell`로 자가 검증을 수행하도록 하는 Reflective Validation 로직 강화
- [x] `agents/coder.py`: 동일 파일에 대한 3회 이상 수정 실패 시 `analyst` 노드로 자동 라우팅하여 정밀 진단 및 원인 분석 요청 워크플로우 통합
- [x] `agents/coder.py`: 사고 과정 트리(`thought_tree`) 및 상태 스키마를 최신 규격으로 업데이트하여 시스템 일관성 확보
- [x] `agents/coder.py`: f-string 중괄호 이스케이핑 오류 수정 및 응답 스키마 안정성 강화

### v1.7.5 (Visual Latency & Cost Tracking UI)
- [x] `ui/dashboard.py`: 사이드바 `USAGE STATS` 패널에 실시간 '평균 지연 시간(Avg Latency)' 표시 항목 추가
- [x] `main.py`: 각 노드별 실행 시간을 누적하여 평균값을 계산하고 UI에 전달하는 실시간 프로파일링 연동
- [x] `ui/dashboard.py`: 지연 시간에 따른 상태 색상(Green/Yellow/Red) 변화 로직을 적용하여 시스템 응답성 시각화
- [x] `main.py`: 세션 전체의 토큰 비용과 지연 시간을 통합 관리하여 운영 효율성 모니터링 강화

### v1.7.4 (Performance Profiler & Cost Analysis)
- [x] `core/observer.py`: 각 노드 실행 시 지연 시간(ms)과 상세 토큰 사용량을 기록할 수 있도록 프로파일링 스키마 확장
- [x] `main.py`: 메인 루프 내에서 노드별 실행 시간을 정밀 측정하고 관찰자에게 실시간 기록하도록 통합
- [x] `core/observer.py`: `trace.jsonl` 로그 파일에 입력/출력 토큰 구분 및 레이턴시 정보를 포함하여 향후 최적화 데이터 기반 마련
- [x] `main.py`: 작업 완료 시 세션 ID와 함께 외부 채널 알림 메시지에도 소요 시간 정보를 포함하도록 개선 검토 기반 마련

### v1.7.3 (Deep Integrity Check & Cache Healing)
- [x] `utils/tools.py`: 프로젝트 전체 파일의 해시를 디스크와 동적으로 비교하여 불일치를 찾아내는 `deep_integrity_check` 로직 구현
- [x] `main.py`: 시스템 부팅 및 세션 시작 시 자동 무결성 검사를 수행하고 캐시를 최신 상태로 자가 수복하도록 통합
- [x] `main.py`: 무결성 검사 결과를 대시보드 시스템 메시지로 출력하여 사용자에게 파일 변경 감지 알림 제공
- [x] `utils/tools.py`: 파일 삭제 케이스에 대한 캐시 자동 정리 로직 추가 및 안정성 강화

### v1.7.2 (Context Compression & Token Optimization)
- [x] `utils/memory.py`: 단순 요약이 아닌 IDENTITY, GOAL, PROGRESS 등 구조화된 상태 보존형 압축(Synaptic Compression) 로직 구현
- [x] `utils/memory.py`: 압축 시 `active_constraints`를 명시적으로 주입하여 시스템 제약 조건의 영속성 강화
- [x] `utils/memory.py`: 최근 메시지 3개를 보존하여 작업의 연속성을 확보하는 지능형 메시지 슬라이싱 로직 적용
- [x] `utils/memory.py`: 압축 과정에서 불필요한 메모리 점유를 방지하기 위한 `gc.collect()` 및 저온도(Temperature 0.0) 설정 최적화

### v1.7.1 (Structured Thought Tree Extraction)
- [x] `agents/manager.py`: 사고 과정을 분석, 추론, 결정 단계로 구조화하는 `thought_tree` 응답 스키마 도입
- [x] `agents/planner.py`: 설계 과정을 분석, 설계, 검증 계획으로 세분화하는 트리 구조 사고 로직 구현
- [x] `ui/dashboard.py`: 트리 구조의 사고 데이터를 수용하고 웹 대시보드로 스트리밍하는 인터페이스 확장
- [x] `main.py`: 에이전트 스트리밍 루프에서 구조화된 트리 데이터를 추출하여 UI에 전달하도록 통합

### v1.7.0 (Gortex Web Dashboard Lite)
- [x] `ui/web_server.py`: FastAPI 및 WebSockets를 활용한 실시간 데이터 스트리밍 서버 구축
- [x] `ui/dashboard.py`: 터미널과 웹 서버 양쪽으로 UI 상태(Chat, Thought, Stats)를 동시 브로드캐스팅하는 로직 구현
- [x] `main.py`: 메인 루프 실행 시 웹 서버를 백그라운드 스레드로 자동 시작하도록 통합
- [x] `ui/dashboard.py`: 중복 코드 제거 및 들여쓰기 오류 수정을 통한 UI 시스템 안정화

### v1.6.9 (Multi-Channel Notifications)
- [x] `utils/notifier.py`: Webhook을 통해 Slack 및 Discord로 실시간 메시지를 전송하는 알림 시스템 구축
- [x] `main.py`: 사용자가 수동으로 상태 보고를 전송할 수 있는 `/notify [message]` 명령어 구현
- [x] `main.py`: 에이전트가 모든 계획된 단계를 성공적으로 완료했을 때 외부 채널로 자동 축하 알림 전송 로직 통합

### v1.6.8 (Git Auto-Deploy & Synchronization)
- [x] `utils/git_tool.py`: Git 명령어 실행 및 저장소 상태 파악을 위한 전용 유틸리티 클래스 신설
- [x] `main.py`: 현재 변경 사항을 스테이징, 커밋, 푸시까지 일괄 처리하는 `/deploy` 명령어 구현
- [x] `main.py`: 배포 전 `git status`를 통한 변경 사항 요약 제공 및 자동 생성된 의미 있는 커밋 메시지 적용

### v1.6.7 (Security Scout & Vulnerability Scanning)
- [x] `agents/trend_scout.py`: `requirements.txt`를 읽고 주요 패키지의 알려진 보안 취약점(CVE)을 검색하는 `check_vulnerabilities` 구현
- [x] `agents/trend_scout.py`: 검색된 취약점 정보를 분석하여 위험 수준(Severity)과 패치 권고안을 생성하는 로직 추가
- [x] `agents/trend_scout.py`: 발견된 보안 경고를 `tech_radar.json`에 기록하여 영구적인 보안 추적 관리 지원
- [x] `agents/trend_scout.py`: 트렌드 스캔과 보안 점검을 병렬로 실행하여 성능 최적화

### v1.6.6 (Project Bundling & Export)
- [x] `main.py`: 현재 프로젝트의 소스 코드와 설정을 ZIP 파일로 압축하는 `/bundle` 명령어 구현
- [x] `main.py`: `venv`, `.git`, `logs/bundles` 등 불필요한 디렉토리를 압축 대상에서 제외하는 필터링 로직 적용
- [x] `main.py`: 생성된 번들 파일을 `logs/bundles` 디렉토리에 타임스탬프와 함께 저장하여 이력 관리 지원

### v1.6.5 (Docker Automation & Deployment)
- [x] `utils/docker_gen.py`: 프로젝트의 의존성을 기반으로 최적화된 `Dockerfile` 및 `docker-compose.yml` 생성 엔진 구현
- [x] `main.py`: 컨테이너 기반 배포 환경을 1초 만에 구성하는 `/dockerize` 명령어 추가
- [x] `utils/docker_gen.py`: Python slim 이미지를 활용하여 경량화된 배포 이미지 구성 및 볼륨 마운트 설정 자동화

### v1.6.4 (Synaptic Map Visualization)
- [x] `utils/indexer.py`: 모듈 간 `import` 관계 및 클래스 상속 구조를 추출하는 `generate_map` 로직 추가
- [x] `main.py`: 프로젝트의 아키텍처를 계층적으로 시각화하는 `/map` 명령어 구현
- [x] `main.py`: `rich.tree.Tree`를 활용하여 모듈, 클래스, 함수 간의 포함 관계를 미려하게 출력

### v1.6.3 (Auto-Dependency Resolution)
- [x] `utils/tools.py`: `execute_shell`에서 `pip install` 명령어 감지 시 패키지명을 `requirements.txt`에 자동 추가하는 기능 구현
- [x] `agents/coder.py`: `ModuleNotFoundError` 발생 시 의존성을 설치하고 `requirements.txt`를 확인하도록 오류 대응 매뉴얼 고도화
- [x] `utils/tools.py`: 중복 패키지 추가 방지 및 대소문자 구분 없는 의존성 체크 로직 강화

### v1.6.2 (Synaptic Search UI & Interaction)
- [x] `main.py`: 사용자가 코드 인덱스를 직접 쿼리할 수 있는 `/search [query]` 명령어 구현
- [x] `main.py`: 검색 결과를 `rich.table.Table`을 활용하여 파일명, 라인, 심볼 타입, 독스트링 요약과 함께 시각화
- [x] `main.py`: 클래스(Blue)와 함수(Green)를 색상으로 구분하여 가독성 향상 및 최대 15개 결과 제한 적용

### v1.6.1 (Context-Aware Reasoning)
- [x] `agents/planner.py`: 사용자의 요청과 관련된 심볼(클래스/함수)의 위치 및 정의 정보를 인덱스에서 검색하여 프롬프트에 자동 주입
- [x] `agents/planner.py`: 파일 경로를 명시하지 않은 요청에 대해서도 인덱스 정보를 바탕으로 정확한 대상 파일을 타겟팅하도록 지침 강화
- [x] `agents/planner.py`: 메시지 포맷(Tuple/Object) 호환성 보강으로 시스템 안정성 확보

### v1.6.0 (Synaptic Indexing Engine)
- [x] `utils/indexer.py`: AST(Abstract Syntax Tree) 분석을 통해 Python 코드의 클래스 및 함수 정의를 추출하는 인덱서 구현
- [x] `main.py`: 부팅 시 프로젝트 코드를 자동 인덱싱하고 `logs/synaptic_index.json`으로 구조화된 데이터 저장
- [x] `main.py`: 수동 재인덱싱 명령어 `/index` 구현
- [x] `utils/indexer.py`: 인덱싱된 데이터를 바탕으로 키워드 및 독스트링 검색이 가능한 `SynapticSearch` 기능 추가

### v1.5.9 (LLM Status & Load Visualization)
- [x] `core/auth.py`: 현재 활성 LLM 제공업체 정보를 반환하는 `get_provider` 메서드 추가
- [x] `ui/dashboard.py`: 사이드바 `SYSTEM STATUS` 패널에 현재 사용 중인 LLM(Gemini/OpenAI) 정보 표시
- [x] `ui/dashboard.py`: 1분당 API 호출 빈도를 시각적 바(Bar) 차트와 색상(Green/Yellow/Red)으로 표시하여 시스템 부하 시각화
- [x] `main.py`: 메인 루프에서 실시간 LLM 상태 정보를 UI에 전달하도록 로직 통합

### v1.5.8 (Multi-LLM Fallback Bridge)
- [x] `core/auth.py`: Gemini 할당량 소진 시 OpenAI로 즉시 전환하는 폴백 시스템 구축
- [x] `core/auth.py`: Gemini 모델과 OpenAI 모델 간의 자동 매핑 테이블(`gpt-4o`, `gpt-4o-mini`) 구현
- [x] `core/auth.py`: OpenAI 응답을 Gemini Response 객체와 호환되도록 덕타이핑 어댑터 추가
- [x] `core/auth.py`: 안티-봇 지터(Anti-bot Jitter) 로직 유지 및 폴백 상태 전이 안정화

### v1.5.7 (Thought Log Persistence)
- [x] `ui/dashboard.py`: 세션 전체의 사고 과정을 기록하는 `thought_history` 필드 추가 및 추적 로직 구현
- [x] `main.py`: `/export` 시 사고 과정 히스토리를 포함하여 저장하도록 스냅샷 구조 확장
- [x] `main.py`: `/import` 시 마지막 사고 과정을 복구하고, 복구된 데이터에 `[RESTORED]` 태그를 부여하여 시각적 구분 강화

### v1.5.6 (Session Snapshot & Recovery)
- [x] `main.py`: `/export` 명령어로 현재 세션의 대화 내역 및 파일 캐시를 JSON으로 저장하는 기능 구현
- [x] `main.py`: `/import [path]` 명령어로 외부 스냅샷 파일을 로드하여 현재 세션에 주입하는 기능 구현
- [x] `main.py`: `handle_command` 시그니처 개선으로 세션 컨텍스트 접근성 향상

### v1.5.5 (Session Isolation & Persistence)
- [x] `main.py`: `global_file_cache`를 `thread_id` 기반의 `all_sessions_cache`로 개편하여 다중 세션 격리 구현
- [x] `main.py`: 세션 시작 시 해당 스레드의 전용 캐시를 로드하고 종료/중단 시 개별적으로 저장하는 로직 강화
- [x] `main.py`: 세션별 캐시 유효성 검사 및 영속화 안정성 확보

### v1.5.4 (Self-Correction Analysis Engine)
- [x] `agents/analyst.py`: 로그(`trace.jsonl`)를 분석하여 실패 후 성공한 패턴을 감지하는 `analyze_self_correction` 구현
- [x] `agents/analyst.py`: 감지된 패턴을 바탕으로 `EvolutionaryMemory`에 새로운 영구 지침을 자동 등록하는 워크플로우 통합
- [x] `agents/analyst.py`: 데이터 분석, 자가 수정 분석, 피드백 분석의 지능형 분기 로직 강화

### v1.5.3 (Log Filtering & Paging Refinement)
- [x] `main.py`: `/logs [skip] [limit] [filter]` 명령어 확장으로 에이전트명/이벤트별 검색 기능 구현
- [x] `main.py`: 필터링 결과에 따른 동적 테이블 타이틀 및 요약 정보 표시 개선

### v1.5.2 (Operational Resilience & Log Paging)
- [x] `main.py`: `/logs [skip] [limit]` 명령어 구현으로 대규모 로그 브라우징 최적화 및 도움말 추가
- [x] `main.py`: 매 턴 종료 시 및 사용자 중단(`KeyboardInterrupt`) 시 `global_file_cache` 자동 저장 로직 강화
- [x] `main.py`: 원자적 파일 쓰기(`save_global_cache`)를 통한 캐시 데이터 무결성 보장

### v1.5.1 (Visual Polish & Table Refinement)
- [x] `utils/table_detector.py`: 헤더가 없거나 숫자로 된 행에 대한 지능형 감지 및 가상 헤더 생성 로직 보강
- [x] `ui/dashboard.py`: 사이드바 패널의 타이틀 및 테두리에 에이전트 전용 스타일 적용 고도화
- [x] `ui/dashboard.py`: 에이전트 상태 관리를 위한 `last_agent` 추적 및 UI 동기화 로직 추가
- [x] `tests/test_ui.py`: 강화된 테이블 감지 로직에 대한 검증 완료

### v1.5.0 (Evolutionary GC & System Cleanup)
- [x] `core/evolutionary_memory.py`: 사용 빈도가 낮고 오래된 규칙을 자동으로 삭제하는 `gc_rules` 기능 구현
- [x] `main.py`: 부팅 시 및 매 턴마다 불필요한 규칙 및 캐시를 정리하는 시스템 최적화 로직 통합
- [x] `main.py`: 코드 구조 정리 및 중복 로직(API 카운트, 메모리 인스턴스) 제거
- [x] `main.py`: 문법 오류(Docstring quotes) 전수 조사 및 수정

### v1.4.9 (Cache Persistence & History Optimization)
- [x] `main.py`: `global_file_cache`를 `logs/file_cache.json`에 영속화하고 부팅 시 자동 복구하는 로직 구현
- [x] `ui/dashboard.py`: 대화가 길어질 경우 성능 유지를 위해 전체 메시지 리스트를 50개로 제한(Cleanup)하는 로직 추가
- [x] `main.py`: 종료 시 파일 캐시 및 기술 레이더 자동 아카이빙 강화

### v1.4.8 (Log Filtering & Self-Modification Loop)
- [x] `main.py`: `/logs [agent] [event] [limit]` 형식의 필터링 명령어 구현으로 대규모 로그 분석 최적화
- [x] `agents/manager.py`: `Optimizer`의 최적화 제안 발견 시 강제로 `Planner`로 라우팅하는 자기 개조 루프 완결
- [x] `main.py`: 로그 필터링 결과 역순(최신순) 표시 및 가독성 개선

### v1.4.7 (Visual Refinement & Coder Intelligence)
- [x] `ui/dashboard.py`: 사이드바 각 패널(Status, Stats, Evolution)의 타이틀 색상을 활성 에이전트 색상과 동기화하여 시각적 일관성 강화
- [x] `agents/coder.py`: 'Standard Error Response Manual'에 Python 구문 오류 해결을 위한 3단계 체크리스트 추가
- [x] `ui/dashboard.py`: 패널 타이틀에 동적 스타일링 적용 로직 고도화

### v1.4.6 (Adaptive Throttling & Log Rotation)
- [x] `core/auth.py`: `GortexAuth`를 싱글톤 패턴으로 변경하여 전역 API 호출 빈도 추적 통합
- [x] `core/state.py`: `GortexState`에 `api_call_count` 필드 추가
- [x] `main.py`: 매 턴 시작 시 최근 API 호출 빈도를 상태에 주입하는 로직 구현
- [x] `agents/manager.py`: API 호출 빈도가 높을 경우(`> 10/min`) 자동으로 더 가벼운 모델(`flash-lite`)을 사용하는 능동적 스로틀링 도입
- [x] `core/observer.py`: `trace.jsonl` 로그 파일이 10MB 초과 시 자동으로 롤링(백업)하는 로직 추가
- [x] `tests/test_auth.py`: 싱글톤 인스턴스 초기화 로직에 맞춘 단위 테스트 수정

### v1.4.5 (Async Responsiveness & Auth Monitoring)
- [x] `agents/researcher.py`: 대규모 웹 스크래핑 루프 내 `asyncio.sleep(0)` 주입으로 UI 갱신 반응성 확보
- [x] `core/auth.py`: 최근 1분간의 API 호출 횟수를 실시간으로 추적하는 `call_history` 모니터링 로직 구현
- [x] `core/auth.py`: 초과 호출 시 경고 로그를 통해 `Optimizer`가 인지할 수 있는 기반 마련

### v1.4.4 (Table Detection Polish & UI Progress)
- [x] `utils/table_detector.py`: Markdown 테이블 감지 로직 고도화 (구분선 미포함 또는 불규칙한 공백 대응 강화)
- [x] `ui/dashboard.py`: 도구 실행 `Progress` 바에 `SpinnerColumn` 추가로 시각적 활동성 강화
- [x] `ui/dashboard.py`: 사이드바 패널 높이(ratio) 재조정으로 정보 밀도 최적화

### v1.4.3 (Manual Scout & Workflow Refinement)
- [x] `main.py`: 수동 기술 스캔 명령어 `/scout` 구현 및 `trend_scout` 노드 직접 트리거 로직 추가
- [x] `main.py`: 명령어 처리기(`handle_command`) 반환값 고도화로 흐름 제어 유연성 확보
- [x] `agents/optimizer.py`: 더 구체적이고 실행 가능한 '패치 지시문' 생성을 위한 프롬프트 강화

### v1.4.2 (Resilience UI & Self-Modification Flow)
- [x] `main.py`: 할당량 소진(`Quota Exhausted`) 발생 시, Align.center를 활용한 풀스크린 스타일의 경고 레이아웃 구현
- [x] `agents/planner.py`: 시스템 최적화 제안(Request) 수락 시 타당성 검토 후 즉시 실행 계획에 반영하도록 지침 보강
- [x] `main.py`: 문법 오류 전수 수정 및 비동기 입력 처리 안정화 완료

### v1.4.1 (UI Sophistication & Async Optimization)
- [x] `ui/dashboard.py`: 사이드바 각 패널(Status, Stats, Evolution) 제목에 이모지 추가 및 상태별 테두리 색상 강조 로직 고도화
- [x] `main.py`: 에이전트 스트리밍 중 UI 업데이트 주기(0.01s) 조정 및 제어권 양보 로직 최적화로 반응성 향상
- [x] `ui/dashboard.py`: USAGE STATS 및 EVOLUTION 패널의 동적 스타일링 적용

### v1.4.0 (Log Paging & Cache Recovery)
- [x] `main.py`: `/logs [skip] [limit]` 페이징 명령어 구현으로 대규모 로그 브라우징 최적화
- [x] `main.py`: 시스템 부팅 시 `global_file_cache`의 무결성을 디스크 상태와 대조하여 검증하는 'Cold Start' 로직 추가
- [x] `main.py`: 매 턴 종료 후 에이전트의 로컬 캐시를 전역 캐시와 동기화하여 지식 유지 보장
- [x] `main.py`: 최신 로그부터 보여주는 역순 페이징 UI 적용

### v1.3.9 (FS Integrity & Security Refinement)
- [x] `utils/tools.py`: `execute_shell` 실행 후 `os.listdir` 기반의 원시적인 파일 시스템 변경 감지 로직 구현 (HINT 반환 기능 강화)
- [x] `utils/tools.py`: 보안 경고 메시지를 테스트 가이드에 맞춰 정교화 ("Execution blocked" 명시)
- [x] `tests/test_tools.py`: 셸 명령을 통한 파일 생성 시의 시스템 힌트 감지 단위 테스트 추가 및 통과

### v1.3.8 (Coder IQ Boost & UI Smoothness)
- [x] `agents/coder.py`: 'Standard Error Response Manual' 추가로 ModuleNotFoundError, IndentationError 등에 대한 즉각 대응 지능 강화
- [x] `main.py`: UI 갱신 대기 시간(0.05s) 및 위치 최적화로 에이전트 사고 과정 스트리밍 시각적 부드러움 향상

... (생략)