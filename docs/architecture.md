# Probenest Architecture Documentation

## Overview

Probenest is an Adversarial AI Evaluation & Reliability Platform designed to assess AI applications for quality (accuracy, faithfulness, hallucination, tool usage) and security (prompt injection, jailbreaks, instruction overrides, data leakage, tool abuse).

## Phase 1 Architecture (Foundation)

The current foundational architecture establishes the client-server setup and core infrastructure:

```text
React + Vite Frontend (TypeScript)
            ↓ HTTP GET /health
 FastAPI Backend (Python 3.11+)
            ↓
  SQLite Database Engine
```

### Core Components

1. **Frontend**: React + TypeScript application built with Vite and styled using Tailwind CSS. Provides the landing dashboard and status monitoring.
2. **FastAPI Application**: High-performance REST API providing application health checks, API endpoints, and configuration lifecycle management.
3. **Database Foundation**: SQLite ORM layer powered by SQLAlchemy 2.x for lightweight, local state persistence without external service dependencies.
4. **CLI Framework**: Command Line Interface built with Typer allowing developers to initiate evaluation and red-teaming tasks locally.

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

### Planned System Subcomponents

- **TargetAdapter**: Abstraction layer for interacting with target LLM applications, RAG pipelines, or APIs.
- **EvaluationRunner**: Orchestration engine for dispatching evaluation datasets against target applications.
- **QualityEvaluators**: Rule-based and LLM-assisted metrics for precision, ground-truth alignment, and hallucination detection.
- **RedTeamEngine**: Adversarial payload generator and probe injector to stress-test robustness.
- **ScoreEngine**: Aggregator computing safety indices, quality scores, and regression analysis across test runs.
- **RegressionEngine**: Comparison engine flagging metric drops across model or prompt updates.
