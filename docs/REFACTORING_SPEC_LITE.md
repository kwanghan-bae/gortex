# 🏗️ Gortex Lite Refactoring Specification (v2.0)

**Document Status**: Draft
**Author**: Jules (AI Agent)
**Date**: 2025-12-28
**Related**: `docs/SPEC_CATALOG.md`

---

## 1. 개요 (Overview)
현재 Gortex는 분산 처리와 대규모 Swarm 운영을 염두에 둔 'Heavy Architecture'를 가지고 있습니다. 이는 로컬 개발 환경에서 간단히 사용하려는 사용자에게 높은 진입 장벽(Redis 설치, 복잡한 설정 등)이 됩니다.
본 리팩토링의 목표는 **'Claude Code'나 'Gemini CLI'와 같이 즉시 실행 가능하고(Zero-Config), 가벼우며(Lightweight), 로컬 중심적인(Local-First)** 구조로 전환하는 것입니다.

## 2. 핵심 목표 (Key Objectives)
1.  **No Infrastructure Dependency**: Redis, RabbitMQ 등 외부 인프라 없이 Python 환경만으로 100% 기능 작동 보장.
2.  **Zero-Config Onboarding**: `.env` 파일 수동 생성이나 `gortex init` 과정 없이, 실행 시점에 필요한 정보를 묻거나 기본값 사용.
3.  **Modern CLI UX**: 단순 REPL을 넘어, 진행 상태바(Spinner), 스트리밍 텍스트, 깔끔한 마크다운 렌더링을 지원하는 `rich` 기반 UI 적용.
4.  **Legacy Compatibility**: 기존의 분산 처리(Distributed) 기능은 옵션으로 남겨두고, 기본값을 로컬 모드로 변경.

## 3. 아키텍처 변경 (Architectural Changes)

### 3.1 인프라 추상화 (Infrastructure Abstraction)
현재 `core/mq.py`와 `core/persistence.py`의 Redis 강결합을 제거하고 인터페이스 기반으로 변경합니다.

*   **MessageQueue Interface**:
    *   `BaseMessageBus`: 공통 인터페이스 정의.
    *   `LocalMessageBus` (New): Python `asyncio.Queue` 또는 In-Memory 리스트를 사용한 로컬 구현체 (Default).
    *   `RedisMessageBus`: 기존 Redis 기반 구현체 (Optional).

*   **Storage Interface**:
    *   `BaseStorage`: 공통 인터페이스.
    *   `SqliteStorage` (New Default): 로컬 파일(`~/.gortex/gortex.db`) 기반의 SQLite 저장소.
    *   `RedisStorage`: 기존 분산 저장소.

### 3.2 설정 시스템 개편 (Configuration Overhaul)
`config/settings.py`를 대대적으로 수정하여 '설정 우선 순위'를 재정립합니다.

1.  **Priority**: CLI 인자 > 환경변수(System Env) > `.env` 파일 > 기본값(Defaults).
2.  **Lazy Loading**: API 키 등 민감 정보는 애플리케이션 시작 시점이 아니라, 실제 필요 시점에 확인하고 없으면 사용자에게 프롬프트로 요청.
3.  **Auto-Discovery**: 프로젝트 루트를 자동으로 감지하고, `.gitignore` 등을 자동 파싱하여 컨텍스트에 반영.

### 3.3 CLI 전용 엔진 분리 (Engine Decoupling)
`GortexSystem`은 너무 많은 배경 작업(Trend Scout, Evolution Node 등)을 포함합니다. CLI용 경량 시스템 클래스를 신설합니다.

*   **`GortexCLI` Class**:
    *   필수 요소만 로드: `GortexEngine` (LLM), `ToolRegistry`, `Memory`.
    *   제거/지연 로딩: `TrendScout`, `EvolutionManager`, `DashboardServer`.
    *   직관적인 실행 루프: `Input -> Process (Thought/Act) -> Output`의 동기적 흐름 강화.

## 4. UX/UI 상세 설계 (UX Design)

### 4.1 CLI Layout (Inspired by Claude Code)
```text
> gortex "Analyze this project"

╭── 🧠 Thinking ──────────────────────────────────────────╮
│  Running `ls -R` to understand structure...             │
│  Reading `README.md`...                                 │
╰─────────────────────────────────────────────────────────╯

✅ **Analysis Complete**
This project seems to be a Python-based AI framework...
...
```

*   **Tool Use**: 도구 사용 시 지저분한 로그 대신 `Spinner`와 한 줄 요약 표시.
*   **Streaming**: LLM 답변을 타자기 효과로 스트리밍 출력.
*   **Prompt**: `prompt_toolkit`을 사용하여 멀티라인 입력, 명령어 히스토리, 파일 경로 자동완성 지원.

## 5. 단계별 실행 계획 (Implementation Plan)

### Phase 1: Core Decoupling (기반 공사)
1.  `config/settings.py` 리팩토링: Redis/MQ 설정을 `Optional`로 변경.
2.  `core/mq.py`, `core/persistence.py`: 추상 클래스 도입 및 In-Memory/SQLite 구현체 고도화.
3.  `main.py`: `gortex init` 강제 로직 제거.

### Phase 2: CLI Engine & UX (기능 구현)
4.  `core/cli/interface.py`: `rich` 기반의 새로운 UI 어댑터 구현.
5.  `core/system_lite.py`: 경량화된 `GortexCLI` 클래스 구현.
6.  `cli.py`: `chat` 명령어가 `GortexCLI`를 사용하도록 연결.

### Phase 3: Polish & Integration (마무리)
7.  기존 테스트(`tests/`)가 In-Memory 모드에서 통과하는지 검증.
8.  불필요한 로그 레벨 조정.
9.  최종 릴리스.

---
**Note**: 이 문서는 1차 승인 후 `docs/TECHNICAL_SPEC.md`에 통합될 예정입니다.
