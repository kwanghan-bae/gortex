알겠어.
아래 문서는 **그대로 `docs/`에 넣어서 사용 가능한 수준의 마크다운 명세서**야.
바이브 코딩, gemini-cli, 향후 gortex 자체 에이전트가 **“이 문서 하나만 보고도 모델 조합과 역할을 이해하고 작업”** 할 수 있도록 작성했어.

---

````markdown
# Gortex – Ollama Model Strategy & Selection Guide
**Date:** 2025-12-24  
**Target HW:** Apple Silicon M1 Max  
**Purpose:** Local-first, small-model–based multi-agent system

---

## 1. Goal of This Document

This document defines:

- Which **Ollama models** should be used
- **Why** each model is chosen
- **Which agent uses which model**
- How models **cooperate and fallback**
- How this strategy supports **infinite automation loops**

This document is intended to be:
- Readable by humans
- Executable as **design intent** by LLM-based CLI tools (gemini-cli, etc.)
- Stable across sessions (externalized cognition)

---

## 2. Design Principles

### 2.1 Local-First Constraint
- No cloud dependency
- Must run fully on **M1 Max**
- Favor **7B–8B class** models

### 2.2 Separation of Cognitive Roles
We do NOT use a single “god model”.

Instead:
- Routing / decision → small deterministic model
- Reasoning / planning → medium reasoning model
- Coding → code-specialized model
- Validation → schema-oriented model

---

## 3. Key Insight: FunctionGemma Is NOT a Chat Model

### 3.1 What FunctionGemma Actually Is

- Based on **Google Gemma 3 (270M)**
- Fine-tuned for **function calling & JSON schema output**
- Extremely lightweight
- Deterministic

**FunctionGemma is a tool-router, not a thinker.**

### 3.2 What It Is Good At
- Intent classification
- Function / tool selection
- Strict JSON output
- Schema adherence

### 3.3 What It Is Bad At
- Long reasoning
- Planning
- Coding
- Natural conversation

---

## 4. Recommended Model Stack (Core)

### 4.1 Manager / Router Agent

**Primary**
- `functiongemma:latest`

**Fallback**
- `granite3.1-moe:3b`

**Why**
- High reliability in structured output
- Low latency
- Perfect for routing and decision trees

---

### 4.2 Planner Agent (Task Decomposition)

**Primary**
- `qwen3:8b`

**Fallback**
- `falcon3:7b`

**Why**
- Strong instruction following
- Good reasoning depth
- Stable multi-step planning

---

### 4.3 Coder Agent (Code Generation / Refactor)

**Primary**
- `qwen2.5-coder:7b`

**Secondary**
- `qwen3:8b`

**Why**
- qwen2.5-coder remains superior for actual code writing
- qwen3 complements with broader reasoning

---

### 4.4 Analyst / Reviewer Agent

**Primary**
- `qwen3:8b`

**Secondary**
- `phi3:3.8b`

**Why**
- Logical evaluation
- Error detection
- Tradeoff analysis

---

### 4.5 Researcher / Summarizer Agent

**Primary**
- `falcon3:7b`

**Secondary**
- `phi3:3.8b`

**Why**
- Fast summarization
- Good signal extraction
- Lower compute cost

---

## 5. Lightweight Utility Models

Used for preprocessing, filtering, token counting, etc.

- `smollm2:1.7b`
- `granite3.1-moe:3b`

---

## 6. Model Decision Tree (Canonical)

```text
IF task == "route / decide / choose tool"
    → functiongemma
ELSE IF task == "plan / decompose / reason"
    → qwen3:8b
ELSE IF task == "write or modify code"
    → qwen2.5-coder:7b
ELSE IF task == "review / critique / score"
    → qwen3:8b
ELSE IF task == "summarize / research"
    → falcon3:7b
ELSE
    → granite3.1-moe
````

---

## 7. Why This Works Well for Infinite Loops

### 7.1 Deterministic Core

* FunctionGemma ensures **stable routing**
* Prevents drift in long-running loops

### 7.2 Reasoning Is Isolated

* Reasoning models don’t decide structure
* They only operate *within* decisions

### 7.3 Failure Is Contained

* If a planner fails, it doesn’t break routing
* If a coder fails, planner context survives

---

## 8. Quantization & Performance Notes (M1 Max)

Recommended:

* `q4_K_M` for 7B–8B models
* `q8_0` for FunctionGemma (cheap enough)

Avoid:

* > 14B models (context thrash, swap risk)

---

## 9. Explicit Non-Goals

This system does NOT aim to:

* Compete with GPT-4/5 class models
* Do “one model does everything”
* Hide complexity

It explicitly favors:

* Transparency
* Restartability
* Session resilience

---

## 10. Summary

* **FunctionGemma is essential**, but only in the correct role
* **qwen3:8b** is the backbone reasoning model
* **qwen2.5-coder:7b** remains best for code
* This stack is **realistic, stable, and loop-safe**

This document is the authoritative source for model selection in Gortex.

---
