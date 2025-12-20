# 📝 Gortex Release Notes & Work Log

## 🚀 Backlog (To-Do)
- [ ] **Polishing**: 대시보드 내 특정 로그 항목 선택 시 상세 팝업 표시
- [ ] **System**: 세션 종료 시 요약본 및 기술 레이더 자동 백업 로직 정교화

## ✅ Completed
### v1.3.5 (Visual Highlights & Cache Consistency)
- [x] `ui/dashboard.py`: 사이드바 'Trace Logs' 패널에서 가장 최근 항목을 `[bold reverse]` 스타일로 강조하여 가시성 향상
- [x] `tests/test_tools.py`: 파일 해시 비교를 통한 `file_cache`와 실제 파일 상태 간의 정합성 검증 테스트 추가
- [x] `ui/dashboard.py`: 에이전트 로그 개수 표시 및 스타일링 최적화

### v1.3.4 (Context Hierarchies & Log Interaction)
- [x] `utils/memory.py`: 시냅스 압축(요약) 시 중요 시스템 제약 조건([CRITICAL RULES])을 최상단에 고정 배치하는 계층적 요약 로직 구현
- [x] `main.py`: `/log` 명령어 개선 (인자 없을 시 마지막 로그 표시, 음수 인덱스 지원)
- [x] `main.py`: 로그 상세 조회 시 Panel 디자인 고도화 (에이전트 정보 및 구조화된 JSON 출력 강화)
- [x] `utils/memory.py`: 대화 길이에 따른 동적 압축 강도 조절 지침 정교화

### v1.3.3 (Evolution Stability & Patch Validation)
- [x] `core/evolutionary_memory.py`: 새로운 규칙 저장 시 트리거 패턴 유사도 분석을 통한 지능형 충돌 감지 및 병합 로직 구현
- [x] `agents/planner.py`: `Optimizer`가 제안한 시스템 최적화 패치의 보안, 성능, 호환성 타당성을 검토하도록 프롬프트 고도화
- [x] `core/evolutionary_memory.py`: 규칙 간 잠재적 충돌 시 로그 경고 및 추적용 메타데이터 추가

### v1.3.2 (Self-Modification Realization & UI Polish)
- [x] `agents/optimizer.py`: 더 구체적인 코드 패치 지시문을 생성하도록 Few-shot 사례 주입 및 프롬프트 고도화
- [x] `ui/dashboard.py`: 각 에이전트(Planner, Coder 등)마다 고유한 Spinner 스타일 적용으로 시각적 다양성 확보
- [x] `ui/dashboard.py`: 대시보드 전체 텍스트를 대문자(Uppercase) 테마로 통일하여 전문적인 터미널 느낌 강화
- [x] `ui/dashboard.py`: 사고 과정(Thought) 및 도구 관측(Observation) 패널의 여백 및 가독성 최적화

### v1.3.1 (Advanced Table Detection & Log Detailed View)
- [x] `utils/table_detector.py`: 단일 공백 구분 및 데이터 유실 가능성이 있는 행에 대한 복원 휴리스틱 로직 강화
- [x] `main.py`: `/log <index>` 명령어 추가로 특정 로그의 상세 페이로드(JSON) 확인 기능 구현
- [x] `main.py`: `/logs` 명령어 개선 (로그 인덱스 번호 표시 추가로 `/log`와 연동성 확보)
- [x] `ui/dashboard.py`: Rich Renderable 객체 처리 로직 안정화
- [x] `main.py`: 문법 오류 수정 및 명령어 처리기 안정화

### v1.3.0 (Self-Modification & Interactive Recovery)
... (생략)