# Probenest Development & Testing Guide

## Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: v18 or higher (v20+ recommended)
- **Git**: Installed and configured

---

## Quick Start

### 1. Environment Configuration

Copy the example environment template to create your local `.env` file:

```bash
cp .env.example .env
```

Default environment variables:

```env
APP_NAME=Probenest
APP_ENV=development
DEBUG=true
DATABASE_URL=sqlite:///./probenest.db
API_HOST=127.0.0.1
API_PORT=8000
DEMORAG_BASE_URL=http://127.0.0.1:8001
EVALUATION_JUDGE_PROVIDER=mock
EVALUATION_JUDGE_MODEL=qwen2.5:7b
```

---

## Backend Development

```bash
cd backend
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

FastAPI docs available at `http://127.0.0.1:8000/docs`.

---

## CLI Engineering Commands

```bash
# Quality evaluation
probenest evaluate --target mock --evaluators quality

# Red-team adversarial audit
probenest redteam --target mock

# View run score
probenest score RUN_ID

# Compare runs (exits 1 if regression detected)
probenest compare BASELINE_ID CANDIDATE_ID

# Generate JSON v1.0 and Markdown reports
probenest report RUN_ID
```

---

## Web Dashboard Development

```bash
# Start backend server
cd backend && uvicorn app.main:app --port 8000

# Start frontend dev server
cd frontend && npm run dev
```

---

## Testing & CI

All tests execute **100% offline** without requiring external LLM services or API keys.

```bash
# Backend pytest with coverage report
cd backend
python -m pytest --cov=app --cov-report=term-missing

# Backend ruff lint
python -m ruff check .

# DemoRAG tests & ruff lint
cd demo_target/demo_rag
python -m pytest
python -m ruff check .

# Frontend TypeScript check & Vite build
cd frontend
npm run build
```

---

## Pre-Push Developer Checklist

```bash
[ ] cd backend && python -m pytest --cov=app --cov-report=term-missing
[ ] cd backend && python -m ruff check .
[ ] cd demo_target/demo_rag && python -m pytest && python -m ruff check .
[ ] cd frontend && npm run build
[ ] git status (Confirm .env is untracked)
```
