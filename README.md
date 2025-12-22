# 🧠 GORTEX: The Self-Evolving AI Partner

> **"잊지 않는 지능, 스스로를 고치는 시스템"**
> Gortex는 로컬 환경에서 동작하며, 사용자의 피드백과 스스로의 데이터를 바탕으로 끊임없이 진화하는 차세대 AI 운영 파트너입니다.

[![Gortex Version](https://img.shields.io/badge/version-2.8.4-blue.svg)](./VERSION)
[![Quality: High-Rigor TDD](https://img.shields.io/badge/Quality-High--Rigor%20TDD-green.svg)](./docs/RULES.md)

---

## 🌟 기획자를 위한 Gortex 활용 시나리오

Gortex는 개발자뿐만 아니라 기획자와 제품 관리자에게도 강력한 통찰을 제공합니다.

### 1. "우리 서비스의 기술적 건강 상태는 어떤가요?"
*   **사용 방법**: 터미널에 `/scan_debt`를 입력하세요.
*   **통찰**: 프로젝트 전체의 복잡도와 기술 부채 점수를 한눈에 파악할 수 있습니다. 점수가 높을수록 리팩토링이 시급하다는 뜻입니다.

### 2. "새로운 기능을 추가하려는데, 어디가 영향을 받나요?"
*   **사용 방법**: "A 기능을 수정하면 영향받는 파일을 분석해줘"라고 자연어로 물어보세요.
*   **통찰**: `Planner` 에이전트가 `Impact Radius`를 분석하여 연관된 모듈과 리스크 수준(Low/Medium/High)을 보고합니다.

### 3. "과거에 우리가 정한 규칙들이 잘 지켜지고 있나요?"
*   **사용 방법**: 대화창에 "지금 적용 중인 제약 조건 보여줘"라고 하세요.
*   **통찰**: `Analyst`가 `experience.json`에 저장된, 우리가 과거에 내렸던 모든 의사결정과 규칙들이 현재 작업에 어떻게 반영되고 있는지 알려줍니다.

---

## 🚀 One-Click 시작하기 (기획자용)

복잡한 설치 과정 없이 '딸깍' 한 번으로 시작할 수 있습니다.

### 1. 시스템 기동
터미널에서 아래 명령어를 입력하십시오.
```bash
./start.sh
```
*   가상환경 구축, 필수 패키지 설치, 브라우저 엔진 설정이 **자동으로 진행**됩니다.
*   설정 도중 **Gemini API 키**를 물어보면 입력해주시면 됩니다.

### 2. 인터페이스 안내
*   **왼쪽 패널**: 에이전트와의 실시간 대화 및 작업 결과 확인.
*   **오른쪽 상단**: 현재 활성화된 에이전트 상태 및 리소스(토큰/비용) 사용량.
*   **오른쪽 하단**: 시스템이 학습한 규칙(`Evolution`) 및 아키텍처 건강도.

---

## 🛠️ 핵심 기능 (Core Logic)

1.  **자가 진화 (Evolution)**: 실수를 학습하여 코드를 스스로 수정합니다.
2.  **아키텍처 수호 (Drift Guard)**: 잘못된 의존성 구조를 감시하고 치유합니다.
3.  **지능형 라우팅 (Expert Routing)**: 작업 성격에 따라 최적의 AI 모델(Gemini/Ollama)을 자동 배정합니다.
4.  **철저한 검증 (Strict TDD)**: 모든 코드는 테스트를 통과해야만 시스템에 반영됩니다.

---

## 📚 상세 명령어 가이드 (User Guide)

| 명령어 | 설명 |
| :--- | :--- |
| `/help` | 모든 명령어 사용법 안내 |
| `/status` | 현재 작업 효율 및 에너지 상태 보고 |
| `/search [검색어]` | 코드 내 기술적 심볼 검색 |
| `/map` | 전체 프로젝트 구조를 시각적 트리로 출력 |
| `/scan_debt` | 기술 부채 및 코드 복잡도 정밀 분석 |
| `/mode [mode]` | 화면 레이아웃 변경 (`coding`, `research`, `analyst` 등) |
| `/language [ko\|en]` | 언어 즉시 변경 |

---

## 📜 문서 체계 (Canonical Docs)
*   [`WORKFLOW.md`](./docs/WORKFLOW.md): 어떻게 협업하는가
*   [`SPEC_CATALOG.md`](./docs/SPEC_CATALOG.md): 무엇을 목표로 하는가
*   [`RULES.md`](./docs/RULES.md): 반드시 지켜야 할 원칙

---
*Developed & Evolved by Gortex Autonomous Protocol*
