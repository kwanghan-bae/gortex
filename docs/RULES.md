# 📏 Gortex Project Rules (v3.0)

이 문서는 Gortex 프로젝트 참여 시 준수해야 하는 **하드 규칙(Hard Rules)**입니다.

---

## 1. 코딩 컨벤션 (Python Standards)

### 1.1 스타일 가이드
*   **PEP 8 준수**: 모든 Python 코드는 PEP 8 스타일 가이드를 따릅니다.
*   **Type Hints 필수**: 모든 함수 시그니처와 주요 변수에 Type Hint를 명시해야 합니다.
    *   `def process(data: Dict[str, Any]) -> bool:`
*   **Docstrings**: 모든 모듈, 클래스, 공개 함수에는 Google Style Docstring을 작성합니다.

### 1.2 금지 패턴 (Anti-Patterns)
*   **Wildcard Import**: `from module import *` 절대 금지.
*   **Bare Except**: `except:` 금지. 구체적인 예외(`except ValueError:`)를 명시하거나 `except Exception:` 사용.
*   **Magic Numbers**: 하드코딩된 숫자나 문자열 대신 상수(Constants) 사용.
*   **Global Variables**: 전역 변수 사용 지양 (`state` 딕셔너리 활용 권장).

---

## 2. 테스트 및 품질 보증 (QA)

### 2.1 테스트 필수 (Test Mandatory)
*   모든 주요 로직 변경 시 대응하는 단위 테스트(`tests/`)를 작성하거나 갱신해야 합니다.
*   `pytest`를 사용하여 테스트를 실행하고 통과해야 커밋이 가능합니다.

### 2.2 정적 분석
*   **Linting**: `ruff check .` 명령어로 린트 에러가 없어야 합니다.
*   **Formatting**: 코드 스타일 통일성을 유지합니다.

---

## 3. 커밋 및 문서화 (Git & Docs)

### 3.1 커밋 메시지 규칙
*   **한국어 작성**: 커밋 메시지는 한국어로 명확하게 작성합니다.
*   **형식**: `태그: 설명` (예: `feat: 에이전트 에너지 시스템 구현`, `fix: 무한 루프 버그 수정`)
*   **태그 목록**: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

### 3.2 문서 동기화 (Doc-Sync)
*   **Rule of Thumb**: 코드가 변하면 문서도 변해야 합니다.
*   기능 추가 시 `SPEC_CATALOG.md` 업데이트.
*   설계 변경 시 `TECHNICAL_SPEC.md` 업데이트.

---

## 4. 보안 (Security)
*   **Secrets**: API Key, Password 등 민감 정보는 절대 코드에 하드코딩하지 않습니다. (환경 변수 `.env` 사용)
*   **Safe Shell**: `run_shell_command` 사용 시 파괴적인 명령어(`rm -rf /` 등) 사용에 각별히 주의합니다.