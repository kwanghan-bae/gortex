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

## 2. Quality Assurance (Testing)

### 2.1 Mandatory Unit Tests
*   모든 신규 기능 구현(`write_file`) 또는 로직 수정 시, 반드시 이에 상응하는 **단위 테스트 코드**를 작성하거나 업데이트해야 한다.
*   테스트는 Python 표준 `unittest` 프레임워크를 사용한다.
*   **Test Location**: `tests/test_<파일명>.py`

### 2.2 Test-Driven Continuity
*   테스트가 통과하지 않는 코드는 Repository에 반영할 수 없다. `pre_commit.sh`는 이 과정을 강제한다.

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

---

## 5. Custom Tooling Protocol

*   **자율 도구 제작**: 에이전트는 기존 기능으로 해결하기 어려운 반복적/복잡한 작업이 있을 경우, 스스로 실행 가능한 스크립트나 도구를 제작할 수 있다.
*   **지식 공유 (MANDATORY)**: 도구를 제작한 에이전트는 반드시 `docs/TOOL.md`에 그 용도와 사용법을 기록해야 한다. 기록되지 않은 도구는 Repository에 남길 수 없다.
*   **재활용**: 모든 에이전트는 세션 시작 시 `docs/TOOL.md`를 읽고, 이미 만들어진 도구가 있다면 적극적으로 활용하여 중복 작업을 방지한다.
