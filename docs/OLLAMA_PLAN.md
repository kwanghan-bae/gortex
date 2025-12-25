# Ollama Model Strategy (M1 Max · 2025-12-24)

## Purpose

This document defines the **official local LLM model strategy** for the Gortex project,
based on **Ollama**, optimized for **Apple Silicon M1 Max** environments.

This specification is intended to be:
- Readable by humans
- Interpretable by CLI-based agents (gemini-cli, future gortex CLI)
- Used as an execution contract for automated coding loops (vibe coding)

---

## Environment Assumptions

- Hardware: Apple Silicon **M1 Max**
- Memory: 32GB ~ 64GB Unified Memory
- Inference: Local (offline-capable)
- Runtime: Ollama
- Date baseline: **2025-12-24**

---

## Design Principles

1. **Local-first** (no external API dependency)
2. **Role-based model assignment**
3. **Graceful degradation** (fallback models)
4. **Session-reset safe** (no hidden memory dependency)
5. **Battery / resource aware**

---

## Model Categories Overview

| Category | Goal |
|--------|------|
| Reasoning | Planning, decision making |
| Coding | Code generation, refactoring |
| Lightweight | Fast classification, summarization |
| Utility | Session glue, metadata handling |

---

## Supported Model Families (Ollama)

- Qwen 3 / Qwen 2.5 (Alibaba)
- Falcon 3
- Granite 3.1 MoE (IBM)
- SmolLM2
- (Optional) Vision models (Qwen-VL)

---

## Resource Constraints (M1 Max)

| Model Size | Feasibility |
|----------|-------------|
| < 3B | Excellent |
| 3B – 7B | Good |
| 7B – 8B | Acceptable |
| > 14B | Not recommended |

---

## Official Model Assignments (By Agent Role)

### 1. Manager Agent (Intent / Routing)

**Purpose**
- Task classification
- Intent detection
- Agent routing

**Primary**
- `granite3.1-moe:3b`

**Fallback**
- `smollm2:1.7b`

**Rationale**
- Extremely fast
- Low memory footprint
- MoE efficiency

---

### 2. Planner Agent (Task Decomposition)

**Purpose**
- Convert intent → executable steps
- Generate structured plans (JSON/YAML)

**Primary**
- `qwen3:8b` (or `qwen2.5:7b`)

**Fallback**
- `falcon3:7b`

**Rationale**
- Strong reasoning
- Good structure generation
- Stable long-context behavior

---

### 3. Coder Agent (Implementation)

**Purpose**
- Code generation
- Refactoring
- Bug fixing
- Spec-driven coding

**Primary**
- `qwen3-coder:8b` (or `qwen2.5-coder:7b`)

**Secondary**
- `qwen2.5-coder:7b`

**Utility / Debug**
- `falcon3:7b`

**Rationale**
- Best local coder performance (2025)
- Strong instruction following
- Acceptable speed on M1 Max

---

### 4. Analyst Agent (Review / Evaluation)

**Purpose**
- Code review
- Design critique
- Risk analysis
- Performance evaluation

**Primary**
- `qwen3:8b` (or `qwen2.5:7b`)

**Fallback**
- `qwen2.5:7b`

---

### 5. Researcher Agent (Summarization / Exploration)

**Purpose**
- Documentation summarization
- External knowledge digestion
- Spec condensation

**Primary**
- `falcon3:7b`

**Fallback**
- `smollm2:1.7b`

---

### 6. Utility Agents (Fast Tasks)

**Purpose**
- Log summarization
- Token reduction
- Metadata extraction
- Pre/post-processing

**Models**
- `smollm2:1.7b`
- `granite3.1-moe:3b`

---

## Optional: Vision / Multimodal

**Use only if explicitly required**

- `qwen3-vl:8b`
- `gemma3:1b`

⚠️ Vision models are **not part of the default execution loop**

---

## Installation Reference

```bash
ollama pull qwen3:8b
ollama pull qwen3-coder:8b
ollama pull qwen2.5-coder:7b
ollama pull falcon3:7b
ollama pull granite3.1-moe:3b
ollama pull smollm2:1.7b
```

---

## Execution Policy

### Default Loop

1. Manager → intent classification
2. Planner → task breakdown
3. Coder → implementation
4. Analyst → review
5. Utility → summarize session

---

### Adaptive Fallback Rules

* If model stalls → downgrade to fallback
* If memory pressure detected → switch to lightweight
* If battery < threshold → forbid 8B models

---

## Session Safety Contract

This system assumes:

* **Every session starts cold**
* No hidden memory
* All state must be recoverable from:

    * Spec documents
    * Workflow documents
    * Session log files

---

## Related Documents

* `docs/catalog_spec.md`
* `docs/workflow.md`
* `docs/next_session.md`
* `docs/session_logs/*.md`

---

## Status

* Version: **v1.0**
* Approved for automated execution
* Safe for infinite-loop vibe coding

---

> This document is authoritative.
> Agents MUST follow this model assignment unless explicitly overridden.