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
- [ ] **Interface**: 인덱싱된 프로젝트의 전체적인 관계도를 시각화하는 `/map` 명령어 구현

## ✅ Completed
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