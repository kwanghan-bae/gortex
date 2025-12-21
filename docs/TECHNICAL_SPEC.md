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
    file_cache: Dict[str, str] # {파일경로: 내용해시}
    next_node: Literal[...]  # 다음 노드 (planner, coder, analyst, swarm, optimizer, etc.)
    assigned_model: str      # 할당된 모델 ID
    coder_iteration: int     # Coder 무한 루프 방지 카운터 (Max 30)
    history_summary: str     # 컨텍스트 압축 요약
    active_constraints: List[str] # 동적 주입 제약 조건
    agent_energy: int        # 가상 에너지 (0~100)
    last_efficiency: float   # 최근 작업 효율성 (0~100)
    efficiency_history: List[float] # 효율성 추세 분석용 이력
    agent_economy: Dict[str, Any] # 에이전트 평판/포인트 데이터
```

---

## 3. Agent Specifications & Output Schemas

### 3.1 Manager (The Router)
*   **Role**: 의도 분석, 규칙 주입, 에너지/평판 기반 리소스 할당.
*   **Routing**: 위험도(Risk > 0.7)가 높으면 'swarm' 또는 'optimizer'로 강제 라우팅.

### 3.2 Planner (The Architect)
*   **Rule**: 코드를 수정하는 단계가 포함되면 반드시 `tests/test_*.py` 작성 단계를 추가해야 한다.
*   **Feature**: `diagram_code` 필드에 Mermaid 다이어그램을 생성하여 구조를 시각화한다.

### 3.3 Coder (The Executor)
*   **Loop**: 최대 30회 반복 가능. 
*   **Pattern (CoVe)**: Read -> Edit -> Verify(Execute Shell) -> Self-Correction.
*   **Standard**: 테스트 코드는 반드시 `unittest` 표준을 따른다.

---

## 4. Core Utilities & Tools (`utils/tools.py`)

*   **`write_file` (Atomic)**: 
    1. `filename.tmp`에 쓰기
    2. 원본을 `logs/backups/`로 백업
    3. `os.replace`로 원자적 교체
*   **`execute_shell` (Secure)**: 
    *   블랙리스트 명령어(`rm -rf` 등) 차단 및 타임아웃(300s) 강제.
    *   출력 결과가 5000자를 초과하면 Head/Tail만 남기고 절삭.
*   **`Memory Compression`**: 
    *   메시지가 12개 이상 쌓이면 `gemini-2.5-flash-lite`를 사용하여 구조화된 요약본 생성.

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

