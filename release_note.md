# 📝 Gortex Release Notes & Work Log

## 🚀 Backlog (To-Do)
- [ ] **Researcher**: `agents/researcher.py` 구현
- [ ] **Analyst**: `agents/analyst.py` 구현
- [ ] **TrendScout**: `agents/trend_scout.py` 구현

## ✅ Completed
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
