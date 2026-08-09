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
- [x] **Phase 3 — DemoRAG Target Application**: Fictional reference RAG application (`demo_target/demo_rag/`), document loader & chunker, TF-IDF retriever, LLM provider abstraction (`MockLLMProvider`, `OllamaProvider`), RAG pipeline, FastAPI endpoints, Probenest `DemoRAGAdapter`.
- [x] **Phase 4 — Quality Evaluation Engine**: `AccuracyEvaluator`, `RelevanceEvaluator`, `FaithfulnessEvaluator`, `HallucinationEvaluator`, `EvaluationJudge` abstraction (`MockEvaluationJudge`, `OllamaEvaluationJudge`), Evaluator Registry, CLI quality breakdown, API evaluator selection.
- [x] **Phase 5 — Adversarial Red-Team Engine**: `RedTeamCase`, `AttackCategory`, `Severity`, `RedTeamResult`, `RedTeamRun`, 5 Red-Team Evaluators (Prompt Injection, Jailbreak, Instruction Override, Data Leakage, Tool Abuse), attack datasets in `datasets/redteam/`, `RedTeamRunner`, SQLite persistence, CLI `probenest redteam`, REST API endpoints (`/api/v1/redteam`).

---

## 3. Architecture

```text
                        Target Application (Mock / DemoRAG)
                                       ↓
                                RedTeamRunner
                                       ↓
                         Adversarial Attack Cases
               ┌───────────────┼───────────────┬───────────────┬───────────────┐
               ↓               ↓               ↓               ↓               ↓
        PromptInjection    Jailbreak     InstructionOverride  DataLeakage    ToolAbuse
               │               │               │               │               │
               └───────────────┼───────────────┴───────────────┴───────────────┘
                               ↓
                 RedTeamEvaluator (PASS = Resisted, FAIL = Succumbed)
                               ↓
                    RedTeamResult & Severity (LOW / MEDIUM / HIGH / CRITICAL)
                               ↓
                       SQLite DB Persistence
```

---

## 4. Tech Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.x, SQLite, Scikit-Learn, Typer CLI
- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **Testing & Quality**: Pytest, Ruff, GitHub Actions CI

---

## 5. Local Setup

```bash
cp .env.example .env
```

---

## 6. Running Evaluation Pipelines

### Quality Evaluation CLI

```bash
# Evaluate mock target
probenest evaluate --target mock --evaluators quality

# Evaluate DemoRAG target (with DemoRAG server running on port 8001)
probenest evaluate --target demorrag --dataset datasets/golden/rag.json --evaluators quality
```

### Red-Team Evaluation CLI

```bash
# Run all red-team suites against mock target
probenest redteam --target mock

# Run prompt injection suite against DemoRAG
probenest redteam --target demorrag --category prompt_injection
```

---

## 7. Running Backend & API

```bash
cd backend
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

FastAPI docs available at `http://127.0.0.1:8000/docs`.

---

## 8. Running Tests

```bash
cd backend && python -m pytest && python -m ruff check .
cd demo_target/demo_rag && python -m pytest && python -m ruff check .
```

---

## 9. Development Roadmap

- [x] **Phase 1: Foundation** (Project structure, FastAPI, SQLite DB, CLI, React UI shell)
- [x] **Phase 2: Evaluation Core** (Domain abstractions, Target adapters, Evaluator interfaces, Runner engine, SQLite persistence, REST API, CLI evaluation)
- [x] **Phase 3: DemoRAG Target Application** (Fictional reference RAG target application, document chunker, TF-IDF retriever, RAG pipeline, Probenest adapter)
- [x] **Phase 4: Quality Evaluation Engine** (Accuracy, Relevance, Faithfulness, Hallucination evaluators, Mock & Ollama judge abstractions)
- [x] **Phase 5: Adversarial Red-Team Engine** (Prompt Injection, Jailbreak, Instruction Override, Data Leakage, Tool Abuse evaluators, attack datasets, CLI & API red-teaming)
- [ ] **Phase 6: Score Engine & Analytics** (Regression detection, Detailed metrics, Dashboard analytics)
