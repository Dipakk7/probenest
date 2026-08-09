# Probenest

**Adversarial AI Evaluation & Reliability Platform**

Probenest is a standalone AI evaluation and adversarial testing platform designed to assess AI applications for accuracy, faithfulness, hallucination detection, prompt injection resilience, jailbreaks, data leakage, and tool abuse.

---

## 1. Overview

Probenest provides automated evaluation and red-teaming pipelines for LLMs, RAG systems, and AI agent frameworks. It measures model quality metrics while stress-testing applications against security vulnerabilities and instruction overrides.

---

## 2. Current Status

- [x] **Phase 1 — Foundation**: FastAPI REST backend, SQLite ORM foundation, Pydantic settings, Typer CLI, React + Vite frontend shell, Pytest & Ruff quality tooling.
- [x] **Phase 2 — Evaluation Core**: Domain models (`EvaluationCase`, `TargetResponse`, `EvaluationResult`, `EvaluationRun`), `TargetAdapter` protocol, `Evaluator` protocol, `EvaluationRunner`, SQLite persistence, dataset loader, `MockTargetAdapter`, `ExactMatchEvaluator`, CLI `probenest evaluate`, and REST API endpoints (`/api/v1/evaluations`).

---

## 3. Architecture

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
               EvaluationRun (SQLite DB)
                     │
                     ↓
               FastAPI REST API
                     │
                     ↓
               React Dashboard
```

---

## 4. Tech Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.x, SQLite, Typer CLI
- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **Testing & Quality**: Pytest, Ruff, GitHub Actions CI

---

## 5. Local Setup

### Environment Setup

Copy `.env.example` to create your local `.env`:

```bash
cp .env.example .env
```

---

## 6. Running Backend & API

```bash
cd backend
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

FastAPI docs are available at `http://127.0.0.1:8000/docs`.

---

## 7. Running Evaluation Pipeline

### CLI Evaluation

```bash
probenest evaluate --dataset datasets/golden/example.json
```

### API Evaluation

```bash
curl -X POST http://127.0.0.1:8000/api/v1/evaluations
```

---

## 8. Running Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard access at `http://localhost:5173`.

---

## 9. Running Tests & Linter

```bash
cd backend
python -m pytest
python -m ruff check .
```

---

## 10. Development Roadmap

- [x] **Phase 1: Foundation** (Project structure, FastAPI, SQLite DB, CLI, React UI shell)
- [x] **Phase 2: Evaluation Core** (Domain abstractions, Target adapters, Evaluator interfaces, Runner engine, SQLite persistence, REST API, CLI evaluation)
- [ ] **Phase 3: Quality Engine & DemoRAG** (Accuracy, Faithfulness, Hallucination evaluators, Target integrations)
- [ ] **Phase 4: Red-Team Engine** (Adversarial probes, Injection payloads, Vulnerability scores)
- [ ] **Phase 5: Score Engine & Analytics** (Regression detection, Detailed metrics, Dashboard analytics)
