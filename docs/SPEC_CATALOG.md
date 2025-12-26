# 📘 GORTEX — Canonical Feature Catalog

**Document Role**
이 문서는 **Gortex(Autonomous AI Swarm Framework)가 무엇인지, 어떤 에이전트들로 구성되는지, 어떤 기능을 제공하는지**를 정의하는 **최상위 기준 스펙 문서**입니다.

---

## 1. 시스템 정체성 (System Identity)

### 1.1 Gortex란?
**Gortex는 스스로 코드를 작성, 검증, 실행하며 진화하는 완전 자율형 AI 에이전트 군집(Swarm) 프레임워크입니다.**
사용자의 모호한 요구사항을 구체적인 계획으로 변환하고, 다수의 전문 에이전트가 협업하여 소프트웨어 결과물을 만들어냅니다.

### 1.2 핵심 철학 (Core Philosophy)
*   **Autonomy**: 인간의 개입을 최소화하고, 에이전트 스스로 판단하고 행동한다.
*   **Evolution**: 스스로 코드를 수정하여 자신의 기능을 확장하고 버그를 고친다.
*   **Transparency**: AI의 사고 과정(Thought Process)과 상태를 투명하게 시각화한다.
*   **Stability**: 엄격한 타입 시스템과 테스트 주도 개발(TDD)로 안정성을 보장한다.

---

## 2. 에이전트 카탈로그 (Agent Roster)

### 2.1 Manager (The Orchestrator)
*   **역할**: 사용자 의도 파악, 작업 라우팅, 리소스(토큰/예산) 관리.
*   **특징**: 시스템의 두뇌. 상황에 따라 Swarm 모드나 Optimizer 모드로 전환 결정.

### 2.2 Planner (The Architect)
*   **역할**: 복잡한 작업을 원자적 단계(Step-by-Step)로 분해, 의존성 관리.
*   **특징**: 실행 가능한 구체적인 계획(Plan)을 수립하고 진척도를 추적.

### 2.3 Coder (The Builder)
*   **역할**: 실제 코드 작성, 리팩토링, 버그 수정.
*   **특징**: CoVe(Chain of Verification) 패턴을 사용하여 작성된 코드의 무결성을 스스로 검증.

### 2.4 Analyst (The Reviewer)
*   **역할**: 코드 리뷰, 테스트 결과 분석, 에러 원인 규명(RCA).
*   **특징**: 비판적 시각으로 결과물을 검증하고 품질 보고서를 작성.

### 2.5 Researcher (The Scout)
*   **역할**: 외부 정보 검색(Web Search), 최신 기술 문서 탐색.
*   **특징**: 코딩에 필요한 최신 라이브러리 사용법이나 솔루션을 찾아옴.

---

## 3. 핵심 기능 (Core Features)

### 3.1 Interactive Dashboard
*   **Rich UI**: 터미널 기반의 화려하고 직관적인 대시보드.
*   **Real-time Status**: 에이전트 활동, 에너지 레벨, 비용, 토큰 사용량 실시간 표시.
*   **Thought Tree**: 에이전트의 사고 과정을 트리 구조로 시각화.

### 3.2 Self-Healing & Evolution (v3.4)
*   **Auto-Fix**: 실행 중 에러 발생 시 스스로 원인을 분석하고 코드를 수정하여 재시도.
*   **Swarm Debugging**: 복잡한 장애 발생 시 분야별 전문가 에이전트들을 소집하여 토론을 통해 최적의 패치 안을 도출.
*   **Super Rules**: Swarm 합의안을 '초월적 규칙'으로 승격 저장하여 시스템 지능을 영구적으로 확장.
*   **Memory Persistence**: 세션 간 기억을 유지하여 과거의 실수를 반복하지 않음.

### 3.4 Neural Governance & Architecture (v7.0)
*   **Neural Constitution**: 시스템의 근본 철학을 정의하는 최상위 가이드라인. 모든 에이전트의 사고와 행동을 윤리적/안전적으로 정렬(Alignment).
*   **Neural Fusion**: 고도로 협업하는 에이전트 쌍을 분석하여 하나의 '엘리트 융합 에이전트'로 병합, 시스템 효율성 극대화.
*   **Weighted Consensus**: 에이전트의 평판과 신뢰도에 기반한 가중 투표 시스템으로 합리적 군집 의사결정 수행.
*   **Multi-Sig Security**: 고위험 도구 실행 시 다수 전문가의 실시간 디지털 서명을 요구하는 강력한 보안 통제.

---

## 4. 기술 스택 및 아키텍처
*   **Core**: Python 3.10+, LangGraph (Orchestration).
*   **LLM**: Google Gemini (Primary), OpenAI/Ollama/LM Studio (Fallback/Local).
*   **UI**: Rich (Terminal UI) & FastAPI/WebSockets (Web Dashboard API).
*   **Distributed**: Redis MQ (Pub/Sub, RPC, Lock).
*   **Storage**: JSON/SQLite (Local) & Redis (Global Knowledge Sync).

---

## 5. 참조 문서
*   `docs/TECHNICAL_SPEC.md`: 구체적 기술 명세 (데이터 구조, 클래스)
*   `docs/RULES.md`: 코딩 컨벤션 및 하드 규칙
