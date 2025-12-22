# Gortex Project Rules & Contracts

This document defines **hard rules** enforced by scripts and policy.
These are NOT guidelines. They are contracts.

---

## 0. Agent Identity: The Document Architect
*   에이전트는 단순히 코드를 작성하는 도구가 아니라, **시스템 워크플로우와 문서의 유지보수자(Maintainer)**이다.
*   세션 간의 모든 기억은 오직 `docs/` 내의 파일로만 유지된다. 따라서 **문서 업데이트가 없는 지식 습득은 '기억 상실'과 같다.**
*   에이전트는 현재 규칙이 부적절하다고 판단될 경우, 언제든지 개선안을 제시하고 문서를 수정할 권한을 가진다.

---

## 1. Commit Contract (CRITICAL)

### 1.1 Pre-Commit Check
Before ANY commit, the following script MUST be executed from the `gortex` directory:
```bash
./scripts/pre_commit.sh
```
*   **If the script FAILS** → Commit is **STRICTLY FORBIDDEN**. You must fix all errors first.
*   **If the script SUCCEEDS** → You must follow the commit message guide.
*   **Message Analysis (MANDATORY)**: 에이전트는 스크립트가 출력하는 **모든 메시지(경고, 힌트, Commit Message Guide 등)를 절대로 무시하지 말고 반드시 정독**해야 한다. 성공하더라도 출력된 내용을 바탕으로 현재 저장소의 상태와 품질을 최종 판단해야 한다.

### 1.2 Commit Message Format
Commit messages MUST be written in **Korean** and follow this format:
`type: 상세 설명 (Korean)`

*   **Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
*   **Example**: `feat: 에이전트 협업을 위한 합의 프로토콜 기초 구현 (v2.3.0)`

---

## 2. Quality Assurance (High-Rigor TDD)

### 2.1 Test-First Principle (ABSOLUTE MANDATE)
*   **No Test, No Code**: 어떤 기능도 테스트 코드가 먼저(혹은 동시에) 작성되지 않으면 구현 코드를 작성할 수 없다.
*   **Vibe Coding Defense**: 환각 방지를 위해, 모든 로직은 실행 가능한 테스트 케이스로 "검증된 사실"만 남긴다.
*   **Red-Green-Refactor**:
    1.  실패하는 테스트 작성 (`tests/test_*.py`)
    2.  테스트를 통과하는 최소한의 코드 구현
    3.  리팩토링 및 안정화

### 2.2 Strict Test Existence (CRITICAL)
*   `pre_commit.sh` v1.3에 따라, 수정된 모든 로직 파일(`.py`)은 반드시 대응하는 테스트 파일(`tests/test_*.py`)을 가져야 한다.
*   **테스트 파일 누락 시 커밋은 강제로 차단된다.**
*   단순한 Mocking을 넘어, 실제 동작을 검증하는 **Integration Test** 비중을 늘려야 한다.

### 2.3 Coverage & Edge Cases
*   **Coverage Goal**: 핵심 모듈(core, agents, utils)의 커버리지는 **70% 이상**을 유지해야 한다.
*   **Edge Cases**: 입력값 검증, 예외 처리, 비동기 타임아웃 등 "망가질 수 있는 상황"을 집요하게 테스트하라.

### 2.4 No Placeholders (CRITICAL)
*   **어떠한 상황에서도 소스 코드 내에 `# ...`, `(중략)`, `(생략)` 등의 플레이스홀더를 삽입할 수 없다.**
*   코드를 수정할 때는 반드시 해당 블록의 **전체 로직을 그대로 유지**하거나, 불필요한 부분만 명확히 삭제해야 한다.
*   설명용 텍스트와 실제 코드를 엄격히 구분하라.

---

## 3. Documentation & State Rules

### 3.1 Source of Truth
*   AI 에이전트의 기억보다 **Repository 내부의 문서(`docs/`)**를 우선한다.
*   세션 종료 시 다음 세 파일을 반드시 업데이트해야 세션이 완료된 것으로 간주한다:
    1.  `docs/sessions/session_XXXX.md` (수행 기록)
    2.  `docs/release_note.md` (변경 요약)
    3.  `docs/next_session.md` (다음 작업 연료 주입)

---

## 4. Safety & Automation Rules

### 4.1 Git Integrity
*   모든 파일 I/O는 프로젝트 승인 도구(`utils/tools.py`)를 사용한다.
*   **IDE 설정 배제**: `.idea/`, `.vscode/`, `.DS_Store` 등 개발 환경 및 OS 종속 파일은 절대로 커밋하지 않는다.
*   에이전트는 작업을 시작하기 전 `.gitignore`가 최신 상태인지 확인하고, 필요한 경우 업데이트를 제안해야 한다.

### 4.2 Security Guard
*   시스템 파괴적인 셸 명령(`rm -rf /` 등)은 차단되며, 시도 시 즉시 보안 경고를 발생시킨다.

### 4.3 UI Development Policy (CRITICAL)
*   **Web UI 개발 중단**: React, Three.js, HTML/JS 기반의 모든 Web 인터페이스 개발 및 리팩토링은 무기한 중단한다.
*   **TUI(Terminal UI) 전념**: 모든 UI 관련 역량은 `rich` 라이브러리 기반의 터미널 대시보드 고도화에 집중한다. Web 관련 코드를 추가하거나 복구하려는 시도는 규정 위반으로 간주한다.

---

## 5. Custom Tooling Protocol

*   **자율 도구 제작**: 에이전트는 기존 기능으로 해결하기 어려운 반복적/복잡한 작업이 있을 경우, 스스로 실행 가능한 스크립트나 도구를 제작할 수 있다.
*   **지식 공유 (MANDATORY)**: 도구를 제작한 에이전트는 반드시 `docs/TOOL.md`에 그 용도와 사용법을 기록해야 한다. 기록되지 않은 도구는 Repository에 남길 수 없다.
*   **재활용**: 모든 에이전트는 세션 시작 시 `docs/TOOL.md`를 읽고, 이미 만들어진 도구가 있다면 적극적으로 활용하여 중복 작업을 방지한다.
