# 🧠 System 2 Scratchpad

## Current Objective: Enhance Local CLI Experience & Prepare Agent Foundry
*   **Origin**: Roadmap Phase 1 (Foundation) & Phase 2 (Agent Foundry)
*   **Key Metrics**: UX Smoothness (Diff View), Modularity (DSL design).

## 1. Feature Specification: Rich Diff View
*   **Problem**: Current `SafetyMiddleware` shows raw text difference or just the new content, which is hard to review for large files.
*   **Solution**: Use `rich.syntax` and `difflib` to render a side-by-side or unified diff view in the terminal before asking for confirmation.
*   **Implementation**:
    -   Modify `core/cli/safety.py`.
    -   Compute diff between `read_file(path)` and `new_content`.
    -   Render using `Syntax` with lexer 'diff' or custom coloring.

## 2. Feature Specification: Intelligent Context
*   **Problem**: User manually adds files with `/add`. This is tedious.
*   **Solution**:
    -   Implement `/auto-context` or smart add.
    -   When user mentions a symbol (e.g., `GortexState`), automatically find defining file and add it (with limits).
    -   Use `grep` or simple indexing to find file paths.

## 3. Design: Agent DSL (Draft)
*   **Concept**: Allow users to define agents without touching core code.
*   **File**: `workspace/agents.yaml`
*   **Structure**:
    ```yaml
    agents:
      - name: "FrontendDev"
        role: "coder"
        model: "gemini-1.5-pro"
        system_prompt: "You are a React expert..."
        tools: ["read_file", "write_file", "npm_run"]
        temperature: 0.2
    
    workflow:
      - from: "FrontendDev"
        to: "Reviewer"
        condition: "task_completed"
    ```
*   **Loader**: `core/registry.py` needs to load this YAML and register agents dynamically.

## 4. Immediate Action Items
1.  Implement `DiffViewer` in `core/cli/safety.py`.
2.  Refactor `gortex chat` to support a simple `/agent` command stub.
3.  Draft `agents.yaml` parser.