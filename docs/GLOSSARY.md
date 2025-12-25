# 📖 Gortex Glossary (Ubiquitous Language)

이 문서는 Gortex 프로젝트에서 사용되는 **핵심 용어 사전**입니다.

---

## 1. Core Concepts
| 용어 (Term) | 설명 (Description) |
| :--- | :--- |
| **Agent** | 특정 역할(Coder, Planner 등)을 수행하는 LLM 기반의 자율 작업 단위. |
| **Swarm** | 여러 Agent가 협업하여 복잡한 문제를 해결하는 집단 지성 시스템. |
| **GortexState** | 시스템의 현재 상태(대화, 메모리, 변수 등)를 저장하는 전역 데이터 구조. `TypedDict`. |
| **Workflow** | Agent들이 상호작용하는 흐름. LangGraph로 정의됨. |

## 2. Operational Terms
| 용어 (Term) | 설명 (Description) |
| :--- | :--- |
| **Thought** | Agent가 행동하기 전에 수행하는 내적 추론 과정. |
| **Plan** | 목표 달성을 위해 Planner가 수립한 단계별 작업 목록. |
| **Energy** | Agent 활동의 비용을 제어하기 위한 가상의 자원. |
| **Tool** | Agent가 외부 세계와 상호작용하기 위해 사용하는 함수 (예: `read_file`, `run_shell`). |

## 3. System Components
| 용어 (Term) | 설명 (Description) |
| :--- | :--- |
| **Manager** | 사용자의 요청을 분석하고 적절한 Agent에게 작업을 할당하는 라우터. |
| **Coder** | 실제 코드를 작성하고 수정하는 엔지니어 Agent. |
| **Analyst** | 결과를 검증하고 분석 리포트를 작성하는 QA Agent. |
| **Planner** | 작업을 계획하고 순서를 정하는 아키텍트 Agent. |
| **Dashboard** | 터미널에 표시되는 실시간 상태 모니터링 UI (Rich 기반). |