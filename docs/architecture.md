# Probenest Architecture & Data Flow Specification

Probenest is an adversarial AI evaluation and reliability platform built with a modular, decoupled architecture.

---

## 1. System Architecture Diagram

```text
                               PROBENEST PLATFORM
                                       │
                      Target Application (Mock / DemoRAG)
                                       │
                                TargetAdapter
                                       │
                        Evaluation Runner & RedTeamRunner
                                       │
                ┌──────────────────────┴──────────────────────┐
                ↓                                             ↓
         Quality Engine                                Red-Team Engine
   (Accuracy, Relevance,                      (Prompt Injection, Jailbreak,
    Faithfulness, Hallucination)                   Override, Leakage, Tool Abuse)
                │                                             │
                └──────────────────────┬──────────────────────┘
                                       ↓
                                  Score Engine
                                       │
                                Regression Engine
                                       │
                              SQLite Storage Layer
                                       │
                ┌──────────────────────┴──────────────────────┐
                ↓                                             ↓
         Engineering CLI                                FastAPI Backend
   (evaluate, redteam, score,                                 │
    compare, report commands)                          React Web Dashboard
```

---

## 2. Component Layer Responsibilities

### 1. Target Application & Adapter Layer (`app/adapters/`)
The `TargetAdapter` protocol isolates Probenest from target applications:
- `MockTargetAdapter`: Deterministic mock target for offline unit testing and development.
- `DemoRAGAdapter`: Adapter communicating with the reference DemoRAG target application via HTTP.

### 2. Evaluation Core (`app/runner/` & `app/evaluators/`)
- `EvaluationRunner`: Executes test cases against target adapters and invokes registered quality evaluators.
- Quality Evaluators: `AccuracyEvaluator`, `RelevanceEvaluator`, `FaithfulnessEvaluator`, `HallucinationEvaluator`.
- `EvaluationJudge`: Abstraction supporting `MockEvaluationJudge` (deterministic) and `OllamaEvaluationJudge` (local LLM judging).

### 3. Red-Team Engine (`app/redteam/`)
- `RedTeamRunner`: Executes adversarial probe cases against target adapters across 5 attack categories.
- Red-Team Evaluators: `PromptInjectionEvaluator`, `JailbreakEvaluator`, `InstructionOverrideEvaluator`, `DataLeakageEvaluator`, `ToolAbuseEvaluator`.

### 4. Score Engine (`app/scoring/`)
- Computes Quality Score (mean of quality evaluators), Security Score (severity-weighted defense rate: Low=1.0, Medium=1.0, High=1.25, Critical=1.5), and Overall Reliability Score (weighted sum: Quality 50% + Security 50%).
- 100% deterministic with zero LLM calls or network requests.

### 5. Regression Detection Engine (`app/regression/`)
- Compares baseline vs. candidate evaluation runs.
- Computes quality delta, security delta, and overall delta in percentage points (`pp`).
- Classifies test failure transitions (`new_failure`, `fixed_failure`, `persistent_failure`).
- Assigns regression severity (`NONE`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) and triggers alerts when degradation exceeds `0.05`.

### 6. Reporting Engine (`app/reports/`)
- `ReportService`: Assembles complete `RunReport` domain objects.
- `JSONReportGenerator`: Stable JSON schema version `1.0`.
- `MarkdownReportGenerator`: GitHub-friendly Markdown documents.

### 7. Interface Layer
- **CLI (`app/cli.py`)**: Typer CLI supporting `evaluate`, `redteam`, `score`, `compare`, `report` commands with standardized exit codes (`0` = Success/No Regression, `1` = Regression, `2` = Invalid Args, `3` = Runtime Error).
- **REST API (`app/main.py`)**: FastAPI backend serving REST endpoints.
- **Web Dashboard (`frontend/`)**: React + TypeScript + Vite dashboard visualizing evaluation benchmarks, red-team defense rates, score cards, failure tables, and regression alerts.

---

## 3. Data Flow

```text
Dataset JSON → TargetAdapter → Target Response → Evaluator Protocol → EvaluationResult
                                                                          │
                                                                          ↓
RunReport (JSON v1.0 / Markdown) ← ReportService ← ScoreEngine & RegressionEngine ← SQLite ORM
```
