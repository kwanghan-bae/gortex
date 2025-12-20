# Gortex v1.0 Ultimate Technical Specification: Synaptic Orchestration & Evolutionary System

**IMPORTANT: Core Instruction for AI Agents**
> 이 문서를 읽는 모든 에이전트는 작업을 시작하기 전 반드시 다음 두 파일을 먼저 읽고 현재 맥락을 파악해야 합니다:
> 1.  **`gortex/release_note.md`**: 전체적인 작업 진행 상황과 To-Do 리스트 확인.
> 2.  **`gortex/next_session.md`**: 이전 세션에서 남긴 구체적인 기술적 맥락과 다음 목표 확인.
>
> **[CRITICAL] Commit Protocol:**
> 1.  **Pre-Commit Check**: 커밋 전 반드시 `gortex/scripts/pre_commit.sh` 실행. (실패 시 커밋 금지)
> 2.  **Documentation**: 작업 완료 시 `gortex/release_note.md`의 해당 항목을 `[x]`로 체크하고, `Completed` 섹션으로 이동.
> 3.  **Confirmation**: `pre_commit.sh` 통과 결과를 사용자에게 보고하고, 커밋 진행 여부를 승인받을 것.

**Version:** 1.1.0 (The Adaptive Edition)
**Codename:** Synaptic Reborn
**Based On:** `KORTEX Reborn v28.0` & `Gortex Preview Specs`
**Core Philosophy:** "Vibe Coding" (Context-Aware, Self-Evolving, Zero-Nagging)

---

## 1. System Identity & Architecture

Gortex is a **Local Operating System-Level AI Partner**. It is designed to be a persistent, evolving entity that lives in your terminal, managing code, executing tasks, and learning from your feedback to avoid repetitive mistakes.

### 1.1 Core Design Patterns
1.  **Hierarchical Multi-Agent Orchestration:** Powered by **LangGraph**. A central `Manager` routes tasks to specialized agents.
2.  **Dual-Key Rotation (The Heart):** A robust authentication engine that rotates between multiple Gemini API keys to bypass rate limits (`429`) and uses anti-bot jitter.
3.  **Evolutionary Memory (The Soul):** A self-learning loop that captures user complaints and converts them into permanent **Constraints** in `experience.json`.
4.  **Active Intelligence (The Eyes):** A `TrendScout` module that searches the internet upon startup to find new models, free APIs, and better agent patterns, keeping the system state-of-the-art.
5.  **Meta-Cognition (The Watcher):** An `Observer` module that logs every "thought" and "tool call" for self-optimization.

### 1.2 Directory Structure (Strict Enforcement)
```text
/gortex
├── .env                    # [CRITICAL] API Keys & Config
├── main.py                 # Application Entry Point (CLI & Graph Runner)
├── setup.sh                # Full Automation Setup Script
├── docker-compose.yml      # Infrastructure (Redis)
├── requirements.txt        # Python Dependencies
├── core/
│   ├── __init__.py
│   ├── auth.py             # Dual Key Rotation & Jitter Engine
│   ├── state.py            # LangGraph State TypedDict
│   ├── graph.py            # Workflow Definition (Conditional Edges)
│   ├── persistence.py      # AsyncSqliteSaver Implementation
│   ├── observer.py         # Structured JSON Logging & Tracing
│   └── evolutionary_memory.py # Feedback Learning Engine
├── agents/
│   ├── __init__.py
│   ├── manager.py          # Intent Router & Rule Injector
│   ├── planner.py          # Atomic Step Decomposition
│   ├── coder.py            # 30-Loop Coding Engine with CoVe
│   ├── researcher.py       # Playwright Scraper (Fast-Fail)
│   ├── analyst.py          # Feedback & Data Analyst
│   ├── trend_scout.py      # [NEW] Startup Trend Hunter & Tech Radar
│   ├── optimizer.py        # Self-Healing & Perf Tuning
│   └── evolution_node.py   # Post-Session Rule Update Node
├── utils/
│   ├── __init__.py
│   ├── tools.py            # Atomic File I/O & Secure Shell
│   ├── memory.py           # Context Compression (Gemini Flash-Lite)
│   ├── cache.py            # Redis Singleton Cache
│   └── learning_tools.py   # Knowledge Base Updaters
└── ui/
    ├── __init__.py
    ├── dashboard.py        # Rich Library Layout & Live Render
    ├── dashboard_theme.py  # Color & Style Definitions
    └── evolution_view.py   # Learned Rules Visualization
```

---

## 2. Configuration & Environment (`.env`)

```ini
# --- Identity & Auth ---
GEMINI_API_KEY_1=your_key_1_here
GEMINI_API_KEY_2=your_key_2_here

# --- System Parameters ---
WORKING_DIR=./workspace
LOG_LEVEL=DEBUG
LLM_TEMPERATURE=0.0
# Increased from default 15 to 30 for complex debugging/refactoring loops
MAX_CODER_ITERATIONS=30 

# --- Infrastructure ---
REDIS_URL=redis://localhost:6379
DB_PATH=gortex_sessions.db
EVOLUTION_DB_PATH=experience.json
TECH_RADAR_PATH=tech_radar.json

# --- Tool Config ---
WEB_SEARCH_TIMEOUT_MS=8000 
SHELL_TIMEOUT_S=300

# --- Active Intelligence ---
# How often (in hours) to scan for new models/tech
TREND_SCAN_INTERVAL_HOURS=24
```

---

## 3. Core Modules Implementation Details

### 3.1 Authentication: `core/auth.py` (The Dual-Key Engine)

*   **Class:** `GortexAuth`
*   **Logic:**
    *   Load keys from `.env`.
    *   Maintain `current_index`.
    *   **Method `generate(model, content, config)`:**
        *   Try `client.generate_content`.
        *   **Catch** `429` or `QuotaExhausted`:
            *   Call `switch_account()`.
            *   **Jitter:** `time.sleep(random.uniform(5.5, 12.0))` to evade bot detection.
            *   Retry.
        *   **Catch** `500/503`:
            *   Wait 3s. Retry (Max `len(keys)*2`).

### 3.2 State Management: `core/state.py`

```python
class GortexState(TypedDict):
    # Chat History (LangGraph auto-merges this)
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # Planner Context
    plan: List[str]          # The breakdown of tasks
    current_step: int        # Index of current task
    
    # File System Context
    working_dir: str
    file_cache: Dict[str, str] # Cache file reads to save tokens
    
    # Control Flow & Safety
    next_node: Literal["manager", "planner", "coder", "researcher", "analyst", "trend_scout", "__end__"]
    coder_iteration: int     # Loop Counter (Max 30)
    
    # Advanced Memory
    history_summary: str     # Compressed context from utils/memory.py
    active_constraints: List[str] # Rules injected from Evolution Engine
```

### 3.3 Persistence: `core/persistence.py`

*   **Backend:** `AsyncSqliteSaver` (from `langgraph.checkpoint.sqlite.aio`).
*   **DB File:** `gortex_sessions.db`.
*   **Function:** Saves the state *after every node execution*. Allows resuming sessions.

---

## 4. Agent Specifications (Detailed)

### 4.1 Manager (The Router)
*   **File:** `agents/manager.py`
*   **Model:** `gemini-3-flash-preview` (Reasoning).
*   **Responsibility:**
    1.  **Rule Injection:** Before routing, read `active_constraints` from State.
    2.  **Intent Classification:**
        *   "Analyze this CSV" -> `Analyst`
        *   "Create a script", "Fix bug" -> `Planner` (then `Coder`)
        *   "Find out about X" -> `Researcher`
        *   "Scout for new models" -> `TrendScout`
    3.  **Ambiguity Check:** If unclear, ask user instead of routing.

### 4.2 Planner (The Architect)
*   **File:** `agents/planner.py`
*   **Model:** `gemini-3-flash-preview`.
*   **Prompt Strategy:** "Decompose the user's goal into atomic, verifiable steps."
*   **Output Schema (Strict JSON):**
    ```json
    {
      "thought_process": "User wants a web server. I need to check for existing files first.",
      "goal": "Initialize Flask App",
      "steps": [
        {"id": 1, "action": "list_files", "target": ".", "reason": "Check for collision"},
        {"id": 2, "action": "write_file", "target": "app.py", "reason": "Create entry point"}
      ]
    }
    ```

### 4.3 Coder (The Executor)
*   **File:** `agents/coder.py`
*   **Model:** `gemini-3-flash-preview` (Coding).
*   **Loop:** `max_iterations=30`.
*   **Behavior (Chain of Verification - CoVe):**
    1.  **Read:** Always `read_file` before editing.
    2.  **Edit:** Use `write_file` (Atomic).
    3.  **Verify:** Run `execute_shell` (syntax check, linter, or test).
    4.  **Self-Correction:** If `execute_shell` returns non-zero exit code, **DO NOT** ask user. Read the error, analyze, and apply fix within the loop.

### 4.4 Researcher (The Investigator)
*   **File:** `agents/researcher.py`
*   **Engine:** `Playwright` (Async).
*   **Optimization (Critical):**
    *   **Resource Exclusion:** Block `image`, `stylesheet`, `font`, `media` types. Speed up loading by 5x.
    *   **DOM Cleaning:** Remove `script`, `style`, `nav`, `footer`, `iframe`. Extract text from `article`, `main`, `#content`.
    *   **Timeout:** Hard limit **8000ms**. If a site is slow, skip it.
    *   **Caching:** Use `utils/cache.py` (Redis) to cache URLs for 24h.

### 4.5 Analyst (The Brain & Ear)
*   **File:** `agents/analyst.py`
*   **Two Modes:**
    1.  **Data Mode:** Uses `pandas` to load `.csv`/`.xlsx` and generate insights/charts.
    2.  **Evolution Mode (Feedback Analysis):**
        *   Input: User's complaint + Agent's previous action.
        *   Action: Identify the "Rule" violated.
        *   Output: A JSON structure for `EvolutionNode`.

### 4.6 TrendScout (The Active Intelligence) - [NEW]
*   **File:** `agents/trend_scout.py`
*   **Trigger:** Runs on system startup if `last_scan > 24h` or invoked manually via `/scout`.
*   **Mission:**
    1.  **Model Hunting:** Search "Best free LLM API 2025", "Gemini API updates". Identify if a newer/cheaper/better model exists than what is in `.env`.
    2.  **Tech Watch:** Search "New autonomous agent patterns python", "LangGraph best practices".
*   **Output:** Updates `tech_radar.json`.
*   **Interaction:** If a major update is found (e.g., "Gemini 2.0 released"), prompts the user at startup: *"New model detected. Update configuration?"*

---

## 5. Evolutionary & Tech Memory

### 5.1 User Constraints (`experience.json`)
Allows Gortex to stop making the same mistakes.
```json
[
  {
    "id": "RULE_001",
    "trigger_patterns": ["unit test", "test code"],
    "instruction": "Always generate pytest-compatible unit tests for every new module.",
    "severity": 5,
    "source_session": "session_id_123",
    "created_at": "2024-01-01T12:00:00"
  }
]
```

### 5.2 Tech Radar (`tech_radar.json`) - [NEW]
Stores external knowledge gathered by TrendScout.
```json
{
  "last_scan": "2024-12-21T09:00:00",
  "models": {
    "gemini-3-flash": {"status": "current", "release_date": "2024-12-01"},
    "gemini-4-preview": {"status": "discovered", "note": "Available for free tier"}
  },
  "patterns": [
    {"topic": "Reflection", "url": "https://...", "summary": "Self-correction loop improves code quality by 30%"}
  ]
}
```

---

## 6. Utilities & Tools (`utils/tools.py`)

### 6.1 `write_file` (Atomic)
*   **Spec:** Never overwrite in place.
    1.  Write to `filename.tmp`.
    2.  Backup original `filename` to `logs/backups/filename.TIMESTAMP.bak`.
    3.  `os.replace('filename.tmp', 'filename')`.

### 6.2 `execute_shell` (Secure)
*   **Spec:**
    *   **Blacklist:** `rm -rf`, `mkfs`, `dd`, `fork bomb`.
    *   **Timeout:** 300s.
    *   **Capture:** `stdout` and `stderr`.
    *   **Output Truncation:** If output > 5000 chars, keep head(1000) + tail(1000) + "<truncated>".

### 6.3 `memory.py` (Synaptic Compression)
*   **Trigger:** `len(messages) > 12`.
*   **Logic:**
    1.  Call `gemini-2.5-flash-lite`.
    2.  Prompt: "Summarize conversation: Goal, Done, Todo, Vars."
    3.  Replace `messages[1:-1]` with `SystemMessage(content=summary)`.
    4.  **Important:** Call `gc.collect()` to free Python memory.

---

## 7. Meta-Observability (`core/observer.py`)

*   **FileLoggingCallbackHandler:**
    *   Must be injected into every LangChain/LangGraph node.
    *   Writes to `logs/trace.jsonl`.
    *   Fields: `timestamp`, `trace_id`, `agent`, `event`, `latency_ms`, `token_usage`.

---

## 8. UI & Dashboard (`ui/dashboard.py`)

Powered by **Rich**.

### 8.1 Layout Specification
*   **Split:** Row.
    *   **Left (Main):** Ratio 7. Chat History + Live Agent Thought Stream.
    *   **Right (Sidebar):** Ratio 3.
        *   **Top:** System Status (Current Agent, Step).
        *   **Middle:** Stats (Tokens, Cost, Cache Hits).
        *   **Bottom:** Active Constraints (Evolution Rules).
        *   **Footer:** **Tech Radar Status** (e.g., "Last Scan: 2h ago").

### 8.2 Theme (`ui/dashboard_theme.py`)
```python
GORTEX_THEME = {
    "info": "cyan",
    "warn": "bold yellow",
    "err": "bold red",
    "user": "bold green",
    "ai": "bold blue",
    "system": "dim white",
    "mgr.thought": "italic cyan",
    "cdr.exec": "bold green",
    "radar.new": "bold magenta"
}
```

---

## 9. Deployment (`setup.sh`)

```bash
#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting Gortex Reborn Setup...${NC}"

# 1. Python Check
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed."
    exit 1
fi

# 2. Venv
if [ ! -d "venv" ]; then
    echo -e "${GREEN}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi
source venv/bin/activate

# 3. Dependencies
echo -e "${GREEN}📥 Installing dependencies...${NC}"
pip install --upgrade pip
# Ensure strict versions for stability
pip install google-genai langgraph langchain-core rich playwright beautifulsoup4 redis aiosqlite python-dotenv pandas

# 4. Browsers
echo -e "${GREEN}🌐 Installing Playwright browsers...${NC}"
playwright install chromium

# 5. Dirs
mkdir -p workspace logs/backups skills experience
# Initialize Tech Radar DB if not exists
if [ ! -f "tech_radar.json" ]; then
    echo "{}" > tech_radar.json
fi

echo -e "${BLUE}✨ Setup Complete! Edit .env and run 'python main.py'${NC}"
```

---

## 10. AI Coding Assistant Hand-off (`docs/HANDOFF_PROMPT.md`)

When asking an AI (Cursor, etc.) to write code for Gortex, paste this:

```markdown
# Context: Gortex v1.0 Development
You are building 'Gortex', a local AI OS.
1. **Auth:** ALWAYS use `core.auth.GortexAuth` for LLM calls. Never raw API.
2. **State:** Respect `GortexState` TypedDict.
3. **Tools:** Use `utils.tools` for all I/O. Do not use `open()` directly.
4. **Evolution:** Check `active_constraints` in state before generating text/code.
5. **Active Intelligence:** Implement `agents/trend_scout.py` to update `tech_radar.json`.
5. **UI:** Use `rich.console` for all output. No `print()`.
```

---

## 11. Workflow & Contribution Guidelines

### 11.1 Work Management Files
*   **`gortex/release_note.md`**: Acts as the central **Task Tracker**.
    *   **To-Do**: List planned features or fixes here before starting.
    *   **Done**: Move items here after verification.
*   **`gortex/next_session.md`**: Persists **Context** for continuity.
    *   Save the current state, unresolved issues, and specific instructions for the next AI session here.

### 11.2 Commit Strategy
1.  **Atomic Commits**: Each commit must represent a single, complete logical change.
2.  **Verification First (The "Check" Phase)**:
    *   Execute: `gortex/scripts/pre_commit.sh`
    *   If passed: Report to user ("✅ 모든 테스트 통과했습니다. 커밋할까요?")
    *   If failed: Fix code immediately. DO NOT COMMIT.
3.  **Documentation Update**:
    *   Update `gortex/release_note.md` (Mark as done).
    *   Update `gortex/next_session.md` (Set next goal).
4.  **Commit Messages**:
    *   Language: **Korean (한국어)**.
    *   Tone: Friendly and descriptive.

---

## 12. Continuous Development Guide

This section ensures seamless handover between AI sessions.

### 12.1 How to Command (The "Magic Phrase")
To resume work exactly where it left off, simply type:

> **"@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가."**

### 12.2 What Happens Next?
When this command is issued, the AI Agent must:
1.  **Read `gortex/release_note.md`**: Identify the top item in the **To-Do** list.
2.  **Read `gortex/next_session.md`**: Load the specific context and implementation plan left by the previous session.
3.  **Execute**:
    *   Implement the code.
    *   Verify with tests.
    *   Commit with a Korean message.
    *   Update `release_note.md` (move task to Completed) and `next_session.md` (set next target).

### 12.3 Sample Prompt for Next Session (Copy & Paste)
```markdown
@docs/gortex/SPEC.md 를 읽고 다음 작업을 이어나가.
현재 상태:
- `core/auth.py` 구현 완료.
- 다음 목표: `core/state.py` 및 `utils/tools.py` 구현.

작업 완료 후에는 `release_note.md`를 업데이트하고, 다음 작업자를 위한 `next_session.md`를 작성해줘.
```


