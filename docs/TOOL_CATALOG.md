# Gortex Tool Catalog

이 문서는 Gortex Agent OS에서 사용 가능한 도구들의 목록과 명세를 정의합니다.
Phase 4 업데이트를 통해 에이전트는 파일 시스템을 정밀하게 제어하고 코드를 구조적으로 이해할 수 있는 "Developer Superpowers"를 갖게 됩니다.

## 1. File System Tools (파일 탐색)

### `find_by_name`
- **목적**: 프로젝트 내에서 파일을 이름 패턴으로 빠르게 찾습니다.
- **Arguments**:
    - `pattern` (str): 검색할 파일명 패턴 (예: `*.py`, `**/*.md`). Glob 문법 지원.
    - `path` (str, optional): 검색 시작 경로. 기본값은 현재 디렉토리.
- **특징**: `.gitignore`에 정의된 파일은 자동으로 제외하여 검색 결과를 정제합니다.

### `grep_search`
- **목적**: 파일 내용에 특정 문자열이나 정규식 패턴이 포함된 위치를 찾습니다.
- **Arguments**:
    - `query` (str): 검색할 문자열 또는 정규식.
    - `path` (str, optional): 검색할 디렉토리 또는 파일 경로.
- **특징**: 대소문자 구분 여부 옵션 지원.

---

## 2. Code Editor Tools (코드 편집)

### `replace_file_content`
- **목적**: 파일 내의 특정 코드 블록을 안전하게 교체합니다.
- **Arguments**:
    - `path` (str): 수정할 파일의 절대 경로.
    - `target_content` (str): 교체 대상 원본 코드 (정확히 일치해야 함).
    - `replacement_content` (str): 새로 변경될 코드.
- **안전 장치**:
    - `target_content`가 파일 내에서 유일(Unique)하지 않으면 편집을 거부합니다.
    - 편집 후 Python 파일의 경우 문법(Syntax) 오류를 검사합니다.

### `create_file` (or `write_to_file`)
- **목적**: 새로운 파일을 생성하거나 전체 내용을 덮어씁니다.
- **특징**: 기존 `utils/tools.py`의 `write_file` 기능을 고도화하여 자동 백업 및 히스토리 버전을 관리합니다.

---

## 3. Code Analysis Tools (코드 분석)

### `view_file_outline`
- **목적**: 파일의 전체 구조(클래스, 함수, 메서드 시그니처)를 요약하여 보여줍니다.
- **Arguments**:
    - `path` (str): 분석할 파일 경로.
- **활용**: 파일의 전체 내용을 읽지 않고도 어떤 기능이 있는지 빠르게 파악하여, 에이전트의 컨텍스트 윈도우(Token)를 절약합니다.

### `view_code_item`
- **목적**: 특정 클래스나 함수의 구현부만 선택적으로 읽습니다.
- **Arguments**:
    - `path` (str): 파일 경로.
    - `node_path` (str): 조회할 노드 경로 (예: `MyClass.my_method`).
