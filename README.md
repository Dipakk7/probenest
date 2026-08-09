# Probenest

**Adversarial AI Evaluation & Reliability Platform**

Probenest is a standalone AI evaluation and adversarial testing platform designed to assess AI applications for accuracy, faithfulness, hallucination detection, prompt injection resilience, jailbreaks, data leakage, and tool abuse.

---

## 1. Overview

Probenest provides automated evaluation and red-teaming pipelines for LLMs, RAG systems, and AI agent frameworks. It measures model quality metrics while stress-testing applications against security vulnerabilities and instruction overrides.

> [!NOTE]
> Probenest is currently in active development. **Phase 1 (Foundation)** establishes the core architecture, backend services, SQLite ORM layer, CLI interface, and frontend dashboard shell. Full evaluation engines will be implemented in upcoming phases.

---

## 2. Problem

Modern AI applications suffer from:
- **Unreliable Quality**: Hallucinations, ungrounded responses, and context deviation in RAG systems.
- **Security Vulnerabilities**: Susceptibility to prompt injections, system prompt extraction, and jailbreak vectors.
- **Silent Regressions**: Model updates or prompt tweaks degrading output quality without notice.

Probenest addresses these challenges by offering automated evaluation benchmarks and red-team probe suites.

---

## 3. Current Status (Phase 1)

Phase 1 Foundation includes:
- [x] Python FastAPI REST backend (`GET /health`, OpenAPI specs at `/docs`)
- [x] SQLite database ORM foundation powered by SQLAlchemy 2.x
- [x] Pydantic v2 settings & environment management
- [x] Command Line Interface (`probenest --help`, `probenest evaluate --help`, `probenest redteam --help`, `probenest compare --help`)
- [x] React + TypeScript + Vite frontend with Tailwind CSS
- [x] Automated test suite (Pytest) and Ruff static analysis
- [x] GitHub Actions CI pipeline

---

## 4. Architecture

```text
Target AI Application
        ↓
Evaluation Runner (Phase 2+)
        ↓
Quality Engine + Red-Team Engine (Phase 2+)
        ↓
Score Engine (Phase 3+)
        ↓
     SQLite DB
        ↓
   FastAPI Server
        ↓
  React Dashboard
```

---

## 5. Tech Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.x, SQLite, Typer CLI
- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **Testing & Quality**: Pytest, Ruff, GitHub Actions CI

---

## 6. Project Structure

```text
probenest/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       └── health.py
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   └── logging.py
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── database.py
│   │   │   └── models.py
│   │   │
│   │   ├── models/
│   │   │   └── __init__.py
│   │   │
│   │   ├── services/
│   │   │   └── __init__.py
│   │   │
│   │   ├── cli.py
│   │   └── main.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_config.py
│   │   ├── test_db.py
│   │   └── test_health.py
│   │
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── components/
│   │   ├── pages/
│   │   ├── lib/
│   │   │   └── utils.ts
│   │   ├── types/
│   │   │   └── health.ts
│   │   ├── App.tsx
│   │   ├── index.css
│   │   └── main.tsx
│   │
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── index.html
│
├── datasets/
│   ├── golden/
│   └── redteam/
│
├── demo_target/
├── docs/
│   ├── architecture.md
│   ├── development.md
│   └── evaluation.md
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .env.example
├── .gitignore
├── README.md
└── Makefile
```

---

## 7. Local Setup

### Environment Setup

Copy `.env.example` to create your local `.env`:

```bash
cp .env.example .env
```

---

## 8. Running Backend

```bash
cd backend
python -m pip install -e .
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

FastAPI docs are available at `http://127.0.0.1:8000/docs`.

---

## 9. Running Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard access at `http://localhost:5173`.

---

## 10. Running Tests

```bash
cd backend
pytest
ruff check .
```

---

## 11. CLI

Execute CLI commands:

```bash
probenest --help
probenest evaluate --help
probenest redteam --help
probenest compare --help
```

---

## 12. Development Roadmap

- **Phase 1: Foundation** (Current Phase - Project structure, FastAPI, SQLite DB, CLI, React UI shell)
- **Phase 2: Evaluation Core** (Target Adapters, Evaluation Runners, Quality Evaluators)
- **Phase 3: Red-Team Engine** (Adversarial probes, Injection payloads, Vulnerability scores)
- **Phase 4: Score Engine & Analytics** (Regression detection, Detailed metrics, Dashboard analytics)

---

## 13. Scope Constraints

Phase 1 strictly omits:
- Heavy container/orchestration setups (Docker, K8s, Celery, Redis)
- External databases (PostgreSQL)
- Real AI evaluation models or live target integration
