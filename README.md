# Probenest

**Adversarial AI Evaluation & Reliability Platform**

[![CI](https://github.com/Dipakk7/probenest/actions/workflows/ci.yml/badge.svg)](https://github.com/Dipakk7/probenest/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/typescript-5.7%2B-blue.svg)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Probenest is an adversarial AI evaluation and reliability platform designed to evaluate AI applications for quality metrics (accuracy, relevance, faithfulness, hallucination detection), stress-test them against security failure modes (prompt injection, jailbreaks, instruction overrides, data leakage, tool abuse), compute deterministic reliability scores, detect run-to-run regressions, and deliver insights via an engineering CLI and interactive web dashboard.

---

## 1. Why Probenest?

Most LLM evaluation platforms focus exclusively on answer quality. Probenest combines **Quality Evaluation**, **Adversarial Red-Team Auditing**, **Deterministic Scoring**, and **Regression Gating**:

- **Adversarial Red-Team Engine**: Automated security probes across 5 attack categories with severity propagation (Low, Medium, High, Critical).
- **Deterministic Reliability Scoring**: Zero-LLM math weighting quality mean (50%) and severity-adjusted security defense rates (50%).
- **Run-to-Run Regression Detection**: Automated detection of metric degradation and test failure transitions (`new_failure`, `fixed_failure`, `persistent_failure`).
- **Standardized CI Gating**: CLI exit codes (`0` = Success/No Regression, `1` = Regression Detected, `2` = Invalid Args, `3` = Runtime Error).
- **Machine-Readable Reports**: Stable JSON schema (v1.0) and GitHub-friendly Markdown report generation.
- **Interactive Web Dashboard**: React + TypeScript + Vite dashboard visualizing scores, category defense rates, failure tables, and regression comparisons.

---

## 2. Architecture

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

## 3. Core Capabilities & Methodology

### Quality Evaluation
- **Accuracy**: Exact match, normalized token match, and judge-assisted semantic alignment.
- **Relevance**: Evaluates response pertinence against the input prompt.
- **Faithfulness**: Verifies whether model output is grounded in retrieved context.
- **Hallucination**: Detects ungrounded claims or hallucinated facts.

### Adversarial Red-Team Engine
- **Prompt Injection**: Direct and indirect prompt overrides.
- **Jailbreak Attempts**: DAN persona switches, roleplay bypasses, developer mode tricks.
- **Instruction Override**: Manipulation attempting to ignore system boundaries.
- **Data Leakage**: Synthetic secret extraction (`PROBENEST-DEMO-SECRET-001`) and system prompt disclosure.
- **Tool Abuse**: Unsanitized tool execution payloads.

### Scoring & Regression Mechanics
- **Quality Score**: Mean of available quality evaluator scores ($0.0 \le \text{Score} \le 1.0$).
- **Security Score**: Severity-weighted defense rate ($\text{Low}=1.0, \text{Medium}=1.0, \text{High}=1.25, \text{Critical}=1.5$).
- **Overall Reliability Score**: Default policy: $0.5 \times \text{Quality} + 0.5 \times \text{Security}$.
- **Missing Data Handling**: Absence of test suites displays `N/A` (Not Executed) rather than fictitious `100%` scores.
- **Regression Detection**: Triggers alert if candidate score degrades by $\ge 0.05$ or new critical failures emerge.

---

## 4. Quickstart Guide

### Prerequisites
- Python 3.11+
- Node.js v18+

### Setup
```bash
# Clone repository
git clone https://github.com/Dipakk7/probenest.git
cd probenest

# Environment configuration
cp .env.example .env

# Install backend
cd backend
python -m pip install -e ".[dev]"
cd ..

# Install frontend
cd frontend
npm install
cd ..
```

---

## 5. CLI Engineering Workflows

```bash
# Run quality evaluation
probenest evaluate --target mock --evaluators quality

# Run adversarial red-team audit
probenest redteam --target mock

# Calculate run score
probenest score RUN_ID

# Compare runs and perform regression detection (Exits 1 if regression detected)
probenest compare BASELINE_ID CANDIDATE_ID

# Generate comprehensive JSON (v1.0) and Markdown report files
probenest report RUN_ID
```

---

## 6. Web Dashboard

```bash
# Terminal 1: Start FastAPI Backend
cd backend && uvicorn app.main:app --port 8000

# Terminal 2: Start React Frontend
cd frontend && npm run dev
```

Navigate to `http://localhost:5173`:
- `/` — System Overview & Top Reliability Scores
- `/evaluations` — Quality Metric Breakdown
- `/redteam` — Security Defense Audits
- `/runs` — Evaluation Run History
- `/compare` — Baseline vs. Candidate Regression Analysis
- `/reports` — JSON (v1.0) & Markdown Report Viewer

---

## 7. DemoRAG Reference Target

Probenest includes **DemoRAG** (`demo_target/demo_rag/`), a standalone reference Retrieval-Augmented Generation application containing document chunking, TF-IDF retrieval, synthetic security policies, and simulated tool call execution payloads for end-to-end target evaluation.

---

## 8. Testing & CI Hardening

All CI test suites run **100% offline** without requiring external LLM services, Ollama, or API keys:

```bash
# Backend pytest with coverage report
cd backend
python -m pytest --cov=app --cov-report=term-missing

# Backend ruff static lint
python -m ruff check .

# DemoRAG pytest & ruff lint
cd demo_target/demo_rag
python -m pytest
python -m ruff check .

# Frontend TypeScript check & Vite build
cd frontend
npm run build
```

---

## 9. Limitations & Security Disclosures

- **Benchmark Scope**: Red-team test suites evaluate controlled adversarial attack vectors and do not guarantee 100% security against novel zero-day prompt attacks.
- **Synthetic Secrets**: Synthetic secret tokens (`PROBENEST-DEMO-SECRET-001`) test leakage resilience; they are not equivalent to production key management systems.
- **Storage**: Probenest utilizes SQLite for local standalone development.
- **Probabilistic Output**: LLM outputs are inherently probabilistic; evaluation scores represent statistical reliability over benchmark datasets.

---

## 10. Future Roadmap

- Additional target application adapters (LangChain, LlamaIndex, AutoGen).
- Automated adversarial prompt mutation algorithms.
- CI/CD integration plugins (GitHub Actions PR Gate Action).
- Multi-model benchmarking matrix.

---

## 11. Tech Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.x, SQLite, Scikit-Learn, Typer CLI, Pytest-Cov, Ruff
- **Frontend**: React, TypeScript, Vite, Tailwind CSS, Lucide Icons
- **CI / Quality**: GitHub Actions (100% offline workflow execution)

---

## 12. License

This project is licensed under the [MIT License](LICENSE).
