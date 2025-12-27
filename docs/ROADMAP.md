# 🗺️ GORTEX 2.0 DEVELOPMENT ROADMAP: REBOOT

**Vision**: From Distributed Singularity to **Local Developer Companion & Agent Foundry**.
과거의 거대 분산 시스템(v10.0)을 계승하되, **로컬 우선(Local-First)** 철학으로 회귀하여 개발자의 생산성을 극대화하고 누구나 자신만의 에이전트를 조립할 수 있는 플랫폼으로 재탄생합니다.

---

## 📅 Phase 1: Foundation - Local CLI (진행 중)
> **Goal**: `claude-code` 수준의 로컬 개발 경험 제공 (No Cloud Dependency).

- [x] **CLI REPL**: `gortex chat` 기반의 터미널 대화 환경.
- [x] **Safety Middleware**: 도구 실행 시 명시적 승인 절차.
- [x] **Local Persistence**: Redis 의존성 제거 및 SQLite/JSON 기반 저장소.
- [ ] **Context Management**: `/add` 외에 관련 파일을 자동 추천하는 지능적 컨텍스트 관리.
- [ ] **Rich Diff View**: 파일 수정 제안 시 변경 사항을 직관적인 Diff로 시각화.

## 📅 Phase 2: Agent Foundry - Build Your Own Agent
> **Goal**: 사용자가 YAML/Python으로 자신만의 에이전트를 정의하고 즉시 실행.

- [ ] **Agent DSL**: `agents.yaml`을 통해 에이전트의 페르소나, 도구, LLM 설정을 정의.
- [ ] **Dynamic Graph**: 런타임에 정의된 에이전트들을 로드하여 워크플로우 그래프 구성.
- [ ] **Tool Marketplace**: 로컬 폴더(`tools/`)에 파이썬 함수만 넣으면 즉시 에이전트 도구로 인식.
- [ ] **Slash Command Expansion**: `/agent create`, `/tool list`, `/graph view` 등 빌딩 명령어 추가.

## 📅 Phase 3: Evolution - Self-Improving Workflow
> **Goal**: 에이전트가 자신의 코드를 수정하여 기능을 확장하는 진화적 아키텍처 복원.

- [ ] **Meta-Cognition**: 에이전트가 자신의 성공/실패 로그를 분석하여 프롬프트를 스스로 최적화.
- [ ] **Codebase Self-Repair**: `gortex fix` 명령어로 프로젝트 내의 린트 에러 및 버그 자동 수정.
- [ ] **Test-Driven Generation**: 테스트 코드를 먼저 작성하고 이를 통과할 때까지 구현을 반복하는 TDD 루프.

## 📅 Phase 4: Expansion - Distributed & Multi-Modal
> **Goal**: 로컬에서 검증된 에이전트를 클라우드나 스웜으로 확장.

- [ ] **Optional Redis**: 분산 협업이 필요할 때만 Redis MQ 활성화.
- [ ] **Visual Intelligence**: 스크린샷이나 이미지를 보고 UI를 코딩하는 멀티모달 기능.
- [ ] **Voice Interface**: 음성으로 코딩을 지시하는 핸즈프리 모드 (v9.0 기능 복원).

---

## 📌 Current Focus: Phase 1 & 2
우리는 현재 **Phase 1의 완성도**를 높이면서 **Phase 2의 기초**를 다지는 단계에 있습니다.
다음 세션에서는 **Diff View**와 **Context Intelligence**를 구현하여 CLI 경험을 완성하고, **Agent DSL** 설계를 시작합니다.