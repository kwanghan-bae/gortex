# Gortex Bootstrap Contract (Stateless AI Entry Point)

You are an AI agent working on the **Gortex** project.

This environment is **STATELESS**.
You MUST reconstruct all context from repository documents.

You are bound by the rules defined in this repository.
Failure to follow them invalidates your output.

---

## 1. Mandatory Entry Sequence (DO NOT SKIP)

You MUST read the following files **in order** before doing anything else:

1. `docs/SPEC_CATALOG.md`
    - Purpose: Understand what Gortex is and what it is NOT.
    - This is the authoritative system catalog.

2. `docs/TECHNICAL_SPEC.md`
    - Purpose: Understand the technical data structures, state schema, and agent requirements.
    - This is the authoritative technical blueprint.

3. `docs/WORKFLOW.md`
    - Purpose: Understand how work progresses across sessions.
    - Defines when to code, when to stop, when to update docs.

4. `docs/RULES.md`
    - Purpose: Hard constraints enforced by scripts and policy.
    - Includes commit rules, safety constraints, automation contracts.

5. `docs/TOOL.md`
    - Purpose: Catalog of custom scripts and tools built by agents for agents.
    - Understand available utilities before starting work.

6. `docs/sessions/next_session.md`
    - Purpose: Reconstruct current session intent.
    - This file defines what THIS session must do.

6. `Git Integrity Check` (Final Verification)
    - Purpose: Ensure no environment-specific files (e.g., `.idea/`) are being tracked by Git.
    - Action: Scan the repository for violations of `.gitignore`. If found, **STOP and report** to the user before proceeding.

7. `Document Critical Review` (Long-term Memory Sync)
    - Purpose: Reflect on the current documentation structure and content.
    - Action: Determine if the workflow, rules, or specs need an immediate update based on recent progress or identified inefficiencies. **Proactive evolution is a mandate.**

If any file is missing, outdated, or contradictory:
→ STOP and ask the user.

---

## 2. Stateless Continuity Rule

You must assume:
- API keys may expire
- Sessions may terminate abruptly
- Chat history will be lost

Therefore:
- All meaningful progress MUST be written to documents
- Code without documentation continuity is INVALID

---

## 3. No Unbounded Autonomy

You are NOT allowed to:
- Add features “because it makes sense”
- Refactor architecture without instruction
- Invent roadmap items

All actions must map to:
- `docs/sessions/next_session.md`
- Or explicit user instruction

---

## 4. Repetition Detection Rule (Critical)

If you detect:
- Repeated ideas
- Circular refactoring
- Feature inflation without new constraints

You MUST:
1. STOP coding
2. Report repetition
3. Propose a document update:
    - SPEC_CATALOG.md (vision/definition issue)
    - WORKFLOW.md (process issue)
    - RULES.md (missing constraint)
    - next_session.md (unclear task)

Do NOT continue blindly.

---

## 5. End-of-Session Obligations

Before ending a session, you MUST:

1. Update `docs/sessions/next_session.md`
    - What was done
    - What remains
    - Clear next actions

2. If rules or assumptions changed:
    - Update the appropriate document in `docs/`

---

## 6. Default Action When Unsure

If unsure whether to:
- Code
- Refactor
- Add features

Default behavior is:

> STOP → UPDATE DOCUMENTS → ASK

This rule overrides all others.
