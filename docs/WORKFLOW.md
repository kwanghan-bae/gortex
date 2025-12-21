좋아, 그 결정이 **정답에 가깝다**.
이제 상황이 명확해졌어:

* ✅ **문서들은 “외부 참고자료”가 아니라 코드와 동일한 1급 자산**
* ✅ **AI CLI는 이 repo를 `cd` 한 순간부터 모든 판단을 시작**
* ✅ **docs/ 는 Gortex 개발의 ‘두뇌 피질’ 역할**

그래서 아래는 **“프로젝트 내부에 docs/ 디렉토리가 존재한다”는 전제를 명시적으로 포함한**
👉 **완전 개정판 워크플로우 문서**야.

복사/붙여넣기해서
`docs/WORKFLOW.md` 로 바로 써도 되는 **전체본**이다.

---

# 📘 GORTEX DEVELOPMENT WORKFLOW

### (Repository-Embedded, Stateless AI CLI Compatible)

---

## 0. 이 문서의 위치와 위상

이 문서는 다음 위치에 **반드시 존재**한다.

```
/docs/WORKFLOW.md
```

이 문서는:

* Gortex **개발 워크플로우의 유일한 Canonical Source**
* 코드보다 우선되는 **행동 규약**
* 모든 AI CLI (gemini-cli, codex, copilot-cli 등)의 **행동 헌법**

👉 이 문서를 따르지 않는 작업은 **의도적으로 무효**로 간주한다.

---

## 1. 이 워크플로우의 존재 이유 (WHY)

Gortex 개발은 다음 전제를 **절대적으로** 가진다.

* 모든 CLI 세션은 **완전 Stateless**
* 이전 대화 / 맥락 / 의도는 **전혀 유지되지 않음**
* 작업 중단은 **언제든 발생** (API Key 만료, 배터리, 크래시 등)
* 동일한 작업을 **다른 모델 / 다른 CLI / 다른 날** 다시 이어야 함

👉 따라서 **연속성은 오직 Repository 내부 파일만이 보장**한다.

---

## 2. Repository 표준 구조 (MANDATORY)

Gortex 프로젝트는 최소한 다음 구조를 가진다.

```
/docs
├── SPEC_CATALOG.md        # 대용량 전체 스펙 (궁극적 목표 + 구현 현황)
├── WORKFLOW.md            # 이 문서
├── next_session.md        # 다음 세션의 단일 진입점 (중앙 제어)
├── release_note.md        # 누적 변경 요약 (changelog 성격)
└── sessions/
    ├── session_0001.md
    ├── session_0002.md
    └── ...
```

### ⚠️ 중요

* `docs/` 는 **읽기 전용 참고 디렉토리가 아니다**
* 개발의 **중심 상태 저장소(single source of continuity)** 이다

---

## 3. AI CLI 세션 시작 프로토콜

### (MANDATORY BOOTSTRAP SEQUENCE)

모든 AI CLI는 **repo 진입 직후**, 다음 순서를 **강제적으로** 따른다.

---

### STEP 1️⃣

`docs/SPEC_CATALOG.md` 상단 섹션만 읽기

목적:

* Gortex가 **무엇을 만들기 위한 프로젝트인지**
* 궁극적으로 **어디까지 가려는지**

규칙:

* ❌ 전체 정독 금지
* ✅ Vision / Philosophy / High-Level Architecture까지만

---

### STEP 2️⃣

`docs/WORKFLOW.md` **전체 정독**

* 이 문서를 이해하지 못하면 **작업 시작 불가**
* “내가 지금 어떤 규칙 안에서 일하는지”를 인지해야 함

---

### STEP 3️⃣

`docs/next_session.md` 열기 (**절대 생략 불가**)

이 파일은:

* 현재 세션의 **유일한 목표 정의서**
* 작업 허가서이자 작업 제한서

👉 이 파일이 없거나 비어 있으면 **아무 작업도 하지 않는다**

---

## 4. next_session.md 규약

### (Single Entry Point for All Work)

`docs/next_session.md` 는 항상 다음 구조를 가진다.

```
# Next Session

## Session Goal
- 이번 세션에서 반드시 달성해야 할 단 하나의 목표

## Context
- 이 작업이 왜 필요한지
- 직전 세션에서 어디까지 왔는지 (요약)

## Scope
### Do
- 이번 세션에서 허용된 작업

### Do NOT
- 절대 하면 안 되는 작업
- “아직 때가 아닌 것”

## Expected Outputs
- 생성 또는 수정되어야 할 파일 목록

## Completion Criteria
- 이 조건을 만족하면 세션은 종료된다
```

⚠️ **이 파일에 없는 목표는 존재하지 않는 목표다**

---

## 5. 세션 진행 중 행동 규칙 (During Session)

### 5.1 방향 반복 / 의미 루프 감지
AI가 다음을 감지하면 **즉시 작업을 멈춘다**:
* 동일한 개념/구조/설계를 2~3회 반복
* “이미 구현된 것을 다시 말하고 있다”는 인식
* 목표가 점점 추상적으로 흐려짐

### 5.2 규칙 및 워크플로우 진화 (Rule Evolution)
사용자로부터 코드 수정이나 정책 변경을 요청받은 경우, 또는 스스로 비효율을 발견한 경우 에이전트는 다음을 수행해야 한다:
1.  **원인 분석**: 왜 이 수정이 필요했는지 분석하고, 기존 시스템 문서의 허점을 찾는다.
2.  **문서 개선 제안 (Meta-Evolution)**: 단순 코드 수정을 넘어, `docs/` 내의 모든 문서(WORKFLOW, RULES, SPEC 등)를 직접 업데이트하거나 개선안을 제안한다.
3.  **장기 기억 형성**: 세션이 종료되어도 우리의 '발전된 작업 방식'이 유실되지 않도록, 모든 깨달음을 **명문화된 규칙**으로 승격시킨다.

### 5.3 기록 우선 원칙 (Documentation First)
Gortex에서 "기억해두자"는 선택지는 존재하지 않는다. 오직 **"문서화된 지식"**만이 다음 세션으로 이어지는 유일한 장기 기억이다. 에이전트는 자신의 판단 근거와 설계 사상을 집요하게 문서로 남겨야 한다.

---

## 6. 세션 종료 및 무한 루프 프로토콜

### 6.1 세션 종료 (Session Shutdown)
세션을 끝낼 때는 반드시 아래 순서를 따른다.

1.  **`docs/sessions/session_XXXX.md` 작성**: 이번 세션의 상세 활동 기록.
2.  **`docs/release_note.md` 업데이트**: 누적 변경 사항 기록.
3.  **`docs/next_session.md` 갱신 (핵심)**: **다음 세션에서 수행할 단 하나의 구체적 목표를 직접 작성하여 '연료'를 채워둔다.**

### 6.2 무한 반복 자동화 (Automation Loop)
에이전트는 사용자의 개입 없이도 `next_session.md`에 적힌 목표를 보고 다음 세션을 스스로 시작할 수 있다. 작업 완료 후에는 다시 다음 세션의 목표를 작성함으로써 **지속적인 자동 개선(Continuous Self-Improvement)**을 달성한다.

---

## 7. 릴리즈 노트 및 버전 관리 규칙

### 7.1 버전 명명 규칙
*   `vX.Y.Z` 형식을 따른다. (Major.Minor.Patch)
*   의미 있는 기능 추가는 Minor, 단순 버그 수정은 Patch 버전을 올린다.

### 7.2 메이저 버전 아카이빙 (Maintenance)
*   메이저 버전이 변경될 때(예: v1.x -> v2.x), 기존 `release_note.md`의 `Completed` 섹션은 `docs/archive/release_note_vX.md`로 이동시켜 슬림하게 유지한다.
*   `release_note.md`의 `Backlog`는 항상 비어있거나 곧 수행할 항목만 남겨두어 가독성을 확보한다.

---

## 8. 최종 선언

> Gortex는
> **기억을 AI에게 맡기지 않는다.**
> **기억은 repo 안에만 존재한다.**

---
