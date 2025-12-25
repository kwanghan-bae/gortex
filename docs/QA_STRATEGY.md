# Gortex Quality Assurance & TDD Retrospective

## 1. 최근 버그 원인 분석 (Why TDD Failed?)

최근 발생한 두 가지 주요 버그(`ChainMap Serialization`, `UI Refresh`)가 단위 테스트(Unit Test)를 통과했음에도 실제 환경에서 발생한 이유는 다음과 같습니다.

### 1-1. ChainMap Serialization Error
- **원인**: **"가정의 오류 (Assumption Mismatch)"**
- **내용**: 테스트 코드에서는 State 객체가 평범한 `dict`일 것이라고 가정하고 테스트했습니다. 하지만 실제 `LangGraph` 라이브러리는 내부적으로 `collections.ChainMap` 타입을 사용합니다.
- **교훈**: 외부 라이브러리와 연동되는 경계(Boundary) 지점에서는 Mock 데이터가 아닌, **실제 라이브러리가 생성하는 객체**를 사용하여 테스트해야 합니다.

### 1-2. UI Refresh Issue (/help 무반응)
- **원인**: **"환경적 요소의 부재 (Environment Gap)"**
- **내용**: 단위 테스트는 `handle_command` 함수가 올바른 문자열이나 상태를 반환하는지(Logic)만 검증했습니다. 하지만 문제는 로직이 끝난 후 **`rich.Live`가 화면을 다시 그리는 타이밍(Timing/Side-Effect)**에서 발생했습니다. 이는 정적인 단위 테스트로는 포착하기 어려운 동적인 런타임 이슈입니다.
- **교훈**: UI/TUI 애플리케이션은 로직 테스트 외에도, 실제 실행 루프를 시뮬레이션하는 **통합 테스트(E2E) 스크립트**가 필수적입니다.

## 2. 향후 품질 강화 전략 (Improvement Plan)

위 교훈을 바탕으로 Gortex의 QA 프로세스를 다음과 같이 개선합니다.

### 2-1. Realistic Data Testing (현실적 데이터 도입)
- **Action**: 외부 라이브러리(LangGraph, LangChain 등) 관련 테스트 시, 단순 Dict/Mock 대신 실제 라이브러리 클래스를 인스턴스화하여 테스트 데이터로 주입합니다.
- **Example**: `test_persistence.py`에 `ChainMap`, `BaseMessage` 등 실제 타입 혼합 테스트 케이스 추가.

### 2-2. Integration Verification Scripts (스크립트 기반 검증)
- **Action**: `tests/` 폴더의 단위 테스트 외에, `scripts/` 폴더에 **"재현 및 통합 시나리오 스크립트"**를 적극적으로 운용합니다.
- **Scripts**:
    - `scripts/test_drive.py`: 전체 기능 유기적 연동 테스트
    - `scripts/repro_*.py`: 특정 버그 재현 및 픽스 검증용 (일회성이 아닌 회귀 테스트로 유지)

### 2-3. UI Logic Separation (UI 로직 분리)
- **Action**: `main.py`에 집중된 UI 제어 로직(Rendering loop)과 비즈니스 로직(Command Handling)을 더 철저히 분리하여, UI 렌더링 자체도 모킹 가능한 구조로 리팩토링합니다.

우리는 이 문서를 지침 삼아, '테스트를 위한 테스트'가 아닌 **'실제 동작을 보장하는 테스트'**를 작성할 것을 약속합니다.
