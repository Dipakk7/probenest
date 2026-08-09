# Probenest Architecture Documentation

## Overview

Probenest is an Adversarial AI Evaluation & Reliability Platform designed to assess AI applications for quality (accuracy, faithfulness, hallucination, tool usage) and security (prompt injection, jailbreaks, instruction overrides, data leakage, tool abuse).

---

## Phase 2 Architecture (Evaluation Core)

Phase 2 establishes the core evaluation domain models, runner orchestration, SQLite persistence layer, and deterministic demonstration target/evaluators:

```text
               EvaluationCase
                     │
                     ↓
               TargetAdapter (e.g. MockTargetAdapter)
                     │
                     ↓
               TargetResponse
                     │
                     ↓
               Evaluator (e.g. ExactMatchEvaluator)
                     │
                     ↓
               EvaluationResult
                     │
                     ↓
               EvaluationRun (SQLite Persistence)
```

### Core Architecture Components

1. **Domain Abstractions (`backend/app/domain/`)**:
   - `EvaluationCase`: Represents individual input/expected output evaluation test cases.
   - `TargetResponse`: Encapsulates output text, context, tool calls, and execution metadata.
   - `TargetAdapter`: Protocol interface enabling decoupled interaction with target applications.
   - `Evaluator`: Protocol interface defining evaluation metrics and probes.
   - `EvaluationResult`: Standardized case outcome payload (pass/fail, score, reason, evidence).
   - `EvaluationRun`: Complete run metadata and case results container.

2. **Runner Engine (`backend/app/runner/`)**:
   - `EvaluationRunner`: Orchestrates dispatching evaluation cases against target adapters, invoking generic evaluators, aggregating results, and reporting run completion.

3. **Persistence & Repository Layer (`backend/app/repositories/`)**:
   - `EvaluationRepository`: Manages SQL persistence for `evaluation_runs` and `evaluation_results` in SQLite.
   - `EvaluationService`: High-level application service connecting dataset loading, runner execution, and database storage.

4. **REST API & CLI Interfaces**:
   - CLI: `probenest evaluate --dataset datasets/golden/example.json`
   - API: `POST /api/v1/evaluations`, `GET /api/v1/evaluations`, `GET /api/v1/evaluations/{run_id}`

---

## Planned Architecture (Future Phases)

In upcoming phases, Probenest will incorporate modular evaluation adapters, red-teaming suits, and scoring engines:

```text
Target AI Application (e.g. DemoRAG)
                  ↓
          TargetAdapter
                  ↓
          EvaluationRunner
        ┌─────────┴─────────┐
        ↓                   ↓
 Quality Engine      Red-Team Engine
  - Accuracy          - Injection
  - Faithfulness      - Jailbreak
  - Hallucination     - Data Leakage
        └─────────┬─────────┘
                  ↓
             ScoreEngine
                  ↓
             SQLite DB
                  ↓
              FastAPI
                  ↓
          React Dashboard
```
