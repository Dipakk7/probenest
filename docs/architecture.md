# Probenest Architecture Documentation

## Overview

Probenest is an Adversarial AI Evaluation & Reliability Platform designed to assess AI applications for quality (accuracy, relevance, faithfulness, hallucination, tool usage) and security (prompt injection, jailbreaks, instruction overrides, data leakage, tool abuse).

---

## Phase 4 Architecture (Quality Evaluation Engine)

Phase 4 implements the Quality Evaluation Engine powered by standard quality evaluators and judge abstractions:

```text
                        Target Application (Mock / DemoRAG)
                                       ↓
                                TargetResponse
                                       ↓
                                EvaluationRunner
                                       ↓
                           Quality Evaluator Suite
               ┌───────────────┼───────────────┬───────────────┐
               ↓               ↓               ↓               ↓
       AccuracyEvaluator RelevanceEvaluator FaithfulnessEvaluator HallucinationEvaluator
               │               │               │               │
               └───────────────┼───────────────┴───────────────┘
                               ↓
                       EvaluationJudge (Mock / Ollama)
                               ↓
                       EvaluationResult (Normalized 0.0 - 1.0)
                               ↓
                       SQLite DB Persistence
```

### Core Architecture Components

1. **Quality Evaluators (`backend/app/evaluators/`)**:
   - `AccuracyEvaluator`: Evaluates semantic correctness comparing expected ground truth against target output using layered normalization, fuzzy matching, and judge fallback.
   - `RelevanceEvaluator`: Evaluates how directly the target output addresses the user question, penalizing off-topic generation.
   - `FaithfulnessEvaluator`: Evaluates whether claims in target output are supported by retrieved context snippets (`TargetResponse.context`).
   - `HallucinationEvaluator`: Evaluates grounding and unsupported content risk (Score 1.0 = no hallucination / fully grounded, 0.0 = severe hallucination).

2. **Evaluation Judge Abstraction (`backend/app/judges/`)**:
   - `EvaluationJudge`: Protocol interface defining evaluation judges (`def judge(...)`).
   - `MockEvaluationJudge`: Deterministic offline judge using heuristic rules and regex to score outputs without external LLM calls.
   - `OllamaEvaluationJudge`: Optional Ollama HTTP API judge (`qwen2.5:7b`), parsing JSON responses and handling connection failures gracefully.

3. **Evaluator Registry & Quality Service (`backend/app/evaluators/registry.py` & `backend/app/services/quality_service.py`)**:
   - Resolves metric names (`"accuracy"`, `"relevance"`, `"faithfulness"`, `"hallucination"`, `"quality"`) to evaluator instances and produces metric summaries.

---

## Planned Architecture (Future Phases)

In upcoming phases, Probenest will incorporate red-teaming suits, security scores, regression detection, and dashboard analytics:

```text
Target AI Application (DemoRAG)
           ↓
    EvaluationRunner
    ┌──────┴──────┐
    ↓             ↓
Quality Engine  Red-Team Engine (Phase 5)
    └──────┬──────┘
           ↓
     Score Engine & Analytics (Phase 6+)
           ↓
     React Dashboard
```
