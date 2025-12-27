# 🧠 System 2 Scratchpad

## Current Objective: Bootstrap Local Gortex CLI
*   **Origin**: User Request (Shift from Distributed/Swarm to Local CLI)
*   **Benchmark**: `claude-code` (Primary), `gemini-cli`
*   **Core Philosophy**: State-of-the-art Terminal Experience, Safety-First, Autonomous but Controllable.

## 1. Research Findings & Gap Analysis
| Feature | Claude Code | Gortex (Current) | Gortex (Target MVP) |
| :--- | :--- | :--- | :--- |
| **Interface** | Terminal REPL | Scripts (`main.py`) | `typer` based CLI (`gortex chat`) |
| **Context** | Project-aware | Manual Loading | Auto-index + `/add` command |
| **Safety** | Approval Modes | Basic Prompt | Explicit Permission Logic (y/n) |
| **Tools** | Edit, Run, Commit | Basic Tools | Integrated Toolbelt (Read/Write/Exec) |

## 2. Architecture Design (Local CLI)
*   **EntryPoint**: `cli.py` (using `typer`)
*   **State Management**: `Rich` console for UI, `LangGraph` for agent state.
*   **Safety Layer**: Middleware that intercepts `write_file` and `run_shell_command` to force user confirmation if not in 'Auto' mode.

## 3. Implementation Steps (Atomic)
1.  **Refactor**: Establish `cli.py` as the main entry point.
2.  **UI**: Implement `Rich` based REPL loop.
3.  **Agent**: Connect `Manager` agent to the REPL.
4.  **Tools**: Ensure local tools are correctly wired.
5.  **Test**: Verify atomic file edits and shell execution.

## 4. Risks & Mitigations
*   **Risk**: Infinite loop in REPL. -> **Mitigation**: `Ctrl+C` handler & step limits.
*   **Risk**: Context window overflow. -> **Mitigation**: Implement "Context Pruning" or simple `/clear` command first.
*   **Risk**: Blind execution. -> **Mitigation**: STRICT user confirmation prompt for *every* side-effect tool initially.
