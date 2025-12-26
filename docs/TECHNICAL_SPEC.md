# 🛠️ Gortex Technical Specification (Implementation Blueprints)

**Document Role**
이 문서는 `SPEC_CATALOG.md`의 철학을 뒷받침하는 **구체적인 기술 구현 명세**이다. 모든 에이전트는 코드를 작성하거나 수정할 때 이 문서에 정의된 데이터 구조와 규칙을 준수해야 한다.

---

## 1. Authentication & API Management (`core/auth.py`)

*   **Dual-Key Rotation Engine**: 
    *   여러 개의 Gemini API Key를 로테이션하여 Quota 제한(429)을 우회한다.
    *   **Jitter Logic**: 봇 탐지 방지를 위해 키 전환 시 `random.uniform(5.5, 12.0)`초의 대기 시간을 부여한다.
    *   **Fallback**: Gemini 할당량 소진 시 OpenAI 모델로 즉시 전환하는 멀티 LLM 브리지를 가동한다.

---

## 2. Global State Schema (`core/state.py`)

`GortexState`는 TypedDict로 정의되며, 모든 노드 간 데이터 전달의 유일한 통로이다.

```python
class GortexState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages] # 대화 이력
    plan: List[str]          # Planner가 수립한 원자적 작업 단계들 (JSON 문자열)
    current_step: int        # 현재 실행 중인 단계 인덱스
    working_dir: str         # 현재 작업 디렉토리
    file_cache: Dict[str, Any] # {파일경로: 내용해시}
    next_node: Literal[...]  # 다음 노드 (planner, coder, analyst, swarm, optimizer, etc.)
    assigned_model: str      # 할당된 모델 ID
    coder_iteration: int     # Coder 무한 루프 방지용 카운터 (Max 30)
    step_count: int          # 전체 그래프 실행 단계 카운터 (무한 루프 차단용)
    history_summary: str     # 컨텍스트 압축 요약
    active_constraints: List[str] # 동적 주입 제약 조건
    agent_energy: int        # 가상 에너지 (0~100)
    last_efficiency: float   # 최근 작업 효율성 (0~100)
    efficiency_history: List[float] # 효율성 추세 분석용 이력
    agent_economy: Dict[str, Any] # 에이전트 평판/포인트/스킬 데이터
    is_recovery_mode: bool   # 시스템 장애 복구 모드 활성화 여부
    current_issue: str       # Swarm 토론을 위한 장애 RCA 리포트
    debate_result: Dict[str, Any] # Swarm 합의 결과 데이터
```

---

## 3. Agent Specifications & Output Schemas

### 3.1 Manager (The Router)
*   **Role**: 의도 분석, 규칙 주입, 에너지/평판 기반 리소스 할당.
*   **Routing**: 위험도(Risk > 0.7)가 높으면 'swarm' 또는 'optimizer'로 강제 라우팅.

### 3.2 Planner (The Architect)
*   **Rule**: 코드를 수정하는 단계가 포함되면 반드시 `tests/test_*.py` 작성 단계를 추가해야 한다.
*   **Feature**: `diagram_code` 필드에 Mermaid 다이어그램을 생성하여 구조를 시각화한다.

### 3.4 Neural Governance (v15.0)
*   **System Maturity Index (SMI)**: `(Intel * 0.4) + (Capital * 0.3) + (Trust * 0.3)`. 시스템의 진화 수준을 정량화하는 통합 지표.
*   **Autonomous Drive (`/drive`)**: 사용자의 입력 없이도 스스로 미션을 수립, 오디트, 실행하는 자율 주권 루프.
*   **Galactic Consensus**: 전 지구적 군집 연합 간의 외교 및 합의 투표 시스템.
*   **Neural Seeding**: 지능의 모든 자산을 ZIP 패키지로 아카이빙하고 상속하는 영속성 기술.

---

## 4. 실행 및 배포 (Operations)
*   **Full Cluster Mode**: `./start.sh full` (Master + Worker + API).
*   **Intelligence Inheritance**: `gortex inherit <seed_path>`.
*   **Self-Mission Engine**: `ManagerAgent.self_generate_mission`.
*   **Genesis Reporting**: 세션 종료 시 `GENESIS_REPORT.md` 자동 발행.

---
> "Gortex Specification v15.0: Final Version"

---

## 5. Persistence & Observability

*   **Persistence**: `AsyncSqliteSaver`를 사용하여 노드 실행 직후 상태를 영구 저장한다. (`gortex_sessions.db`)
*   **Observability**: 모든 도구 호출과 에이전트의 "생각"은 `logs/trace.jsonl`에 인과 관계(`cause_id`)와 함께 기록된다.

---

## 6. LLM Abstraction Layer (`core/llm/`)

향후 로컬 모델(Ollama) 도입을 위해 모든 에이전트는 직접 API를 호출하는 대신 추상화된 인터페이스를 사용한다.

*   **`LLMBackend` (ABC)**:
    *   `generate(messages, system_prompt, config) -> LLMResponse` 메서드 정의.
*   **Implementations**:
    *   `GeminiBackend`: 기존의 Dual-Key Rotation 및 Fallback 로직을 포함한다.
    *   `OllamaBackend`: 로컬 서버(`:11434`)와 통신하며, 지정된 경량 모델을 사용한다.
*   **Policy**: 고수준 판단(Manager)은 Gemini를, 단순 반복 작업(Worker)은 Ollama를 우선 할당하는 하이브리드 전략을 취한다.

---

## 7. Multi-Agent Consensus Protocol

복잡도가 높거나 위험한 결정(Risk > 0.7)이 필요한 경우, 시스템은 단일 판단 대신 에이전트 간 토론 과정을 거친다.

### 7.1 Scenario Personas
`swarm` 노드는 다음의 상반된 관점을 가진 시나리오를 병렬 생성해야 한다.
*   **Innovation (The Pioneer)**: 최신 기술 도입, 효율성 극대화, 과감한 구조 개선 중심.
*   **Stability (The Guardian)**: 하위 호환성, 보안 무결성, 운영 안정성, 리스크 최소화 중심.

### 7.2 Consensus Synthesis Schema (`analyst` / `swarm`)
토론 결과는 반드시 다음 JSON 형식을 따라 종합되어야 하며, 합의된 지침은 `is_super_rule=True`로 저장될 수 있다.
```json
{
    "final_decision": "Selected approach or compromise",
    "rationale": "Key reasons for this decision",
    "unified_rule": {
        "instruction": "The single authoritative instruction",
        "trigger_patterns": ["pattern1", "pattern2"],
        "severity": 1-5,
        "category": "coding/research/general"
    },
    "action_plan": ["Step 1: ...", "Step 2: ..."]
}
```

### 7.3 Recovery Reward Multipliers
시스템 장애(is_recovery_mode=True) 상황에서 성공적인 패치를 수행한 에이전트에게는 다음과 같은 가중 보상이 적용된다.
*   **Standard Success**: Difficulty Factor 1.5x
*   **Emergency Recovery Success**: Difficulty Factor 3.0x
*   **Skill Rank Up**: 500pts 단위로 Apprentice -> Journeyman -> Expert -> Master 칭호 부여.

## 8. Plugin-style Agent Registry (v3.0 Architecture)

Gortex v3.0은 에이전트 간의 결합도를 낮추고 확장을 용이하게 하기 위해 **중앙 레지스트리** 기반의 플러그인 아키텍처를 채택한다.

### 8.1 Agent Decoupling
*   모든 에이전트는 `BaseAgent`를 상속받으며, 자신의 능력(Tools)과 역할(Role)을 담은 `AgentMetadata`를 가진다.
*   에이전트는 실행 시점에 `AgentRegistry`에 등록되며, `Manager`는 하드코딩된 노드 이름 대신 레지스트리를 조회하여 작업을 할당한다.

### 8.2 Registry Schema (`core/registry.py`)
```python
class AgentMetadata:
    name: str        # 에이전트 식별자
    role: str        # 담당 역할 (예: 'coder', 'analyst')
    description: str # 상세 설명
    tools: List[str] # 사용 가능한 도구 목록
    version: str     # 에이전트 버전
```

### 8.3 Dynamic Capability Discovery
*   **Capability Discovery**: 특정 도구(예: `git_push`)가 필요한 경우, `Registry`는 해당 도구를 지원하는 가장 적합한 에이전트를 추천할 수 있다.
*   **Version Control**: 동일한 역할의 에이전트라도 버전에 따라 성능이 다를 수 있으며, 평판 데이터와 결합하여 최적의 에이전트를 동적으로 선택한다.


