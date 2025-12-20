# 📝 Gortex Release Notes & Work Log

## 🚀 Backlog (To-Do)
- [ ] **Evolution**: 추출된 규칙 간의 충돌 감지 및 해결 전략 고도화
- [ ] **Data**: 대시보드 내 특정 로그 항목 클릭 시 상세 팝업 표시

## ✅ Completed
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