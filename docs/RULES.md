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

## 🤖 Auto-Evolved Coding Standards

다음은 주어진 규칙을 5가지 원칙으로 요약한 결과입니다:

1. **Python 버전 및 코드 스타일**  
   - Python 3.10+ 사용  
   - PEP8 표준을 준수한 `snake_case` 형식으로 모든 함수 명명  

2. **타입 힌트 사용**  
   - 모든 Python 코드에서 타입 힌트를 필수적으로 사용  

3. **AI 트렌드 모니터링**  
   - 주간으로 최신 AI 트렌드를 확인하고 업데이트  

4. **시스템의 예의와 우선순위**  
   - 시스템이 사용자에게 예의를 지키며 대응  
   - 고유한 우선순위 규칙(`Priority Super Rule`) 적용  

5. **규칙 구조 및 검증**  
   - 규칙의 유형(예: Normal Rule, Certified Rule)을 명확히 구분  
   - 규칙의 유효성과 일관성을 유지 (Merged Rule 포함)  

이 원칙들은 코드 품질, 유지보수성, 기술적 혁신, 시스템의 신뢰성을 강화하는 데 중점을 두고 있습니다.

## 에이전트 동작 원칙 (Antigravity 특화)
- **[계획 우선 (Plan-First)]**: 안티그래비티의 'Mission Control'에서 작업을 시작하기 전, 수정할 모듈과 영향 범위를 기술한 `[작업 설계도]`를 먼저 출력합니다.
- **[코드 생략 절대 금지]**: 에이전트는 절대 코드의 일부를 `...`이나 `// 기존 코드`로 치환하지 않습니다. 전체 컨텍스트를 유지하거나, 명확한 Diff 포맷을 제공합니다.
- **[Self-Testing]**: 코드 수정 후 반드시 `pytest`를 실행하여 기존 로직의 회귀(Regression) 여부를 확인합니다. 특히 M1 Max의 멀티코어 환경에서 레이스 컨디션이 없는지 체크합니다.
- **[추측 금지]**: 파이썬 표준 라이브러리(Standard Lib) 외의 외부 라이브러리 사용 시, 반드시 `pip show`나 문서를 검색하여 정확한 버전을 확인합니다.

## Lesson Record
- 모든 트러블슈팅 결과와 성능 최적화 경험은 `docs/LESSONS_LEARNED.md`에 기록하여, 에이전트가 다음 작업에서 같은 실수를 반복하지 않도록 '지식 베이스'화 합니다.