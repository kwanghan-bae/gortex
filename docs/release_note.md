# Release Notes

## [Unreleased]

### v3.3.0 (2025-12-23)
- **Dynamic Swarm Recruitment**: 고난이도 과제 발생 시, `Economy` 시스템을 조회하여 각 분야(Security, Design 등)의 최고 실력자들을 소집하는 '드림팀' 결성 로직 구현.
- **Expert Debate**: 가상의 페르소나 대신 실제 선발된 에이전트들이 자신의 전문 지식(Role)을 바탕으로 토론하고 해결책을 제시하는 실질적 협업 체계 안착.
- **UI Enhancement**: Swarm 토론 패널에 참여 전문가의 실명과 역할을 시각적으로 구분하여 표시.

### v2.8.5 (2025-12-23)
- **Feature**: LM Studio 연동을 위한 `LMStudioBackend` 구현. `LLM_BACKEND` 환경 변수를 통해 로컬 모델 백엔드를 선택할 수 있으며, 하이브리드 모드 시 Gemini/Ollama 실패 시 자동 폴백합니다.
- **Quality**: 프로젝트 전반에 걸쳐 400개 이상의 린트 에러(복수 구문, 미사용 변수, 잘못된 예외 처리 등)를 수정하여 코드 베이스의 건전성을 대폭 강화했습니다.
- **Testing**: `utils/tools.py`, `utils/economy.py`, `core/auth.py` 등 주요 모듈에 대한 유닛 테스트를 보강하여 커버리지를 확대했습니다.
- **Bug Fix**: `core/auth.py`에서 `get_current_client` 메서드 부재로 인한 벡터 스토어 오류를 수정했습니다.

## ✅ Completed (Recent Milestones)

### v3.2.0 (2025-12-23)
- **Intelligent Routing**: Manager가 작업의 성격을 분석하여 해당 분야의 스킬 점수가 높은 '진짜 전문가'를 선발하는 가중치 기반 라우팅 도입.
- **Mastery Resource Allocation**: Master 등급(스킬 2500+ pts) 에이전트에게는 작업 위험도와 무관하게 고성능 모델(`gemini-1.5-pro`)을 우선 배정하여 품질 보장.
- **Hybrid Scoring**: 전문성(70%)과 평판(30%)을 균형 있게 평가하여 에이전트 선발의 안정성 확보.

### v3.1.0 (2025-12-23)
- **Dynamic Skill Tree**: 에이전트가 작업 성공 시 해당 분야(Coding, Design, Analysis, General)의 숙련도 포인트를 획득하는 성장 시스템 구축.
- **Tool Permissions**: `AgentRegistry`를 통한 도구 권한 강제화. 특정 스킬 등급(Master, Expert 등)에 도달한 에이전트만 `apply_patch` 등 고급 도구 사용 가능.
- **TUI Skill Radar**: 터미널 대시보드에 에이전트별 전문 지표를 시각화하는 'Skill Radar' 위젯 도입.
- **Robustness**: 에이전트 식별 로직의 대소문자 구분 이슈 해결 및 경제 시스템 무결성 강화.

### v2.8.4 (Hybrid Coder & Bounded Execution)
- **Agent**: `agents/coder.py`에 하이브리드 LLM 아키텍처를 적용하여 Gemini와 Ollama를 모두 지원하게 되었습니다.
- **Strategy**: 모델의 Native 기능 지원 여부에 따라 프롬프트 전략과 도구 호출 방식(Native vs Simulated)을 동적으로 전환합니다.
- **Resilience**: 정규식 기반 JSON 추출 로직을 도입하여 로컬 모델의 비정형 응답에 대한 파싱 신뢰도를 높였습니다.

# ... (Previous notes omitted for brevity)