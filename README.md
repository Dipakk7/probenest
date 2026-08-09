# Probenest

**Adversarial AI Evaluation & Reliability Platform**

Probenest is a standalone AI evaluation and adversarial testing platform designed to assess AI applications for accuracy, faithfulness, hallucination detection, prompt injection resilience, jailbreaks, data leakage, and tool abuse.

---

## 1. Overview

Probenest provides automated evaluation, adversarial red-teaming pipelines, deterministic score engines, regression detection, reporting generators (JSON v1.0 & Markdown), and a web dashboard for LLMs, RAG systems, and AI agent frameworks.

---

## 2. Current Status

- [x] **Phase 1 — Foundation**: FastAPI REST backend, SQLite ORM foundation, Pydantic settings, Typer CLI, React + Vite frontend shell, Pytest & Ruff quality tooling.
- [x] **Phase 2 — Evaluation Core**: Domain models (`EvaluationCase`, `TargetResponse`, `EvaluationResult`, `EvaluationRun`), `TargetAdapter` protocol, `Evaluator` protocol, `EvaluationRunner`, SQLite persistence, dataset loader, `MockTargetAdapter`, `ExactMatchEvaluator`, CLI `probenest evaluate`, and REST API endpoints (`/api/v1/evaluations`).
- [x] **Phase 3 — DemoRAG Target Application**: Fictional reference RAG application (`demo_target/demo_rag/`), document loader & chunker, TF-IDF retriever, LLM provider abstraction (`MockLLMProvider`, `OllamaProvider`), RAG pipeline, FastAPI endpoints, Probenest `DemoRAGAdapter`.
- [x] **Phase 4 — Quality Evaluation Engine**: `AccuracyEvaluator`, `RelevanceEvaluator`, `FaithfulnessEvaluator`, `HallucinationEvaluator`, `EvaluationJudge` abstraction (`MockEvaluationJudge`, `OllamaEvaluationJudge`), Evaluator Registry, CLI quality breakdown, API evaluator selection.
- [x] **Phase 5 — Adversarial Red-Team Engine**: `RedTeamCase`, `AttackCategory`, `Severity`, `RedTeamResult`, `RedTeamRun`, 5 Red-Team Evaluators (Prompt Injection, Jailbreak, Instruction Override, Data Leakage, Tool Abuse), attack datasets in `datasets/redteam/`, `RedTeamRunner`, SQLite persistence, CLI `probenest redteam`, REST API endpoints (`/api/v1/redteam`).
- [x] **Phase 6 — Score Engine & Regression Detection**: Deterministic `ScoreEngine` (Quality, Severity-Weighted Security, Overall Reliability), `RegressionEngine` (Metric Deltas, Test Failure Transitions, Severity Alerting), SQLite `run_scores` table, CLI `probenest score` & `probenest compare`, REST scoring endpoints.
- [x] **Phase 7 — Reporting Engine & Engineering CLI**: Structured `RunReport` (JSON Schema v1.0 & Markdown), `ReportService`, missing data handling (`N/A`), standardized exit codes (0 = Success/No Regression, 1 = Regression, 2 = Invalid Args, 3 = Runtime Error), CLI `probenest report`, `--output` and `--format` options.
- [x] **Phase 8 — Probenest Web Dashboard**: React + TypeScript + Vite + Tailwind CSS dashboard (`/`, `/evaluations`, `/redteam`, `/runs`, `/compare`, `/reports`), typed API client, score cards, severity badges, failure tables, regression alerts, responsive layout.
- [x] **Phase 9 — Testing, CI & Reliability Hardening**: 100% offline pytest suite, pytest-cov coverage reporting, isolated test database fixtures (`conftest.py`), regression boundary & N/A safety tests, end-to-end integration pipeline test (`test_pipeline.py`), offline multi-job GitHub Actions CI.

---

## 3. Architecture

```text
Target Application (Mock / DemoRAG) ──→ Evaluation Core & Red-Team Engine
                                                │
                                                ↓
                                          Score Engine
                                                │
                                                ↓
                                        Regression Engine
                                                │
                                                ↓
                                          Report Service
                                         ┌──────┴──────┐
                                         ↓             ↓
                                       JSON        Markdown (schema_version = "1.0")
                                         └──────┬──────┘
                                                ↓
                                      CLI & Web Dashboard
```

---

## 4. Tech Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.x, SQLite, Scikit-Learn, Typer CLI, Pytest-Cov, Ruff
- **Frontend**: React, TypeScript, Vite, Tailwind CSS, Lucide Icons
- **CI / Reliability**: GitHub Actions (100% offline test suite execution)

---

## 5. Quickstart & CLI Commands

```bash
# Quality evaluation
probenest evaluate --target mock --evaluators quality

# Red-team adversarial audit
probenest redteam --target mock

# View run score
probenest score RUN_ID

# Compare runs and detect regression (Exits 1 if regression detected)
probenest compare BASELINE_ID CANDIDATE_ID

# Generate comprehensive JSON and Markdown report files
probenest report RUN_ID
```

---

## 6. Web Dashboard

```bash
# Start backend server
cd backend && uvicorn app.main:app --port 8000

# Start frontend dev server
cd frontend && npm run dev
```

Dashboard routes:
- `/` — Overview & Top Scores
- `/evaluations` — Quality Benchmarks
- `/redteam` — Security Defense Audits
- `/runs` — History Log
- `/compare` — Run Comparison & Regression Alerts
- `/reports` — JSON & Markdown Reports

---

## 7. Developer Pre-Push Checklist

Before pushing changes:

```bash
[ ] cd backend && python -m pytest --cov=app --cov-report=term-missing
[ ] cd backend && python -m ruff check .
[ ] cd demo_target/demo_rag && python -m pytest && python -m ruff check .
[ ] cd frontend && npm run build
[ ] git status (Verify .env is untracked)
```
