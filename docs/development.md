# Probenest Development Guide

## Prerequisites

- **Python**: 3.11 or higher (Python 3.13 supported)
- **Node.js**: v18 or higher (v22 recommended)
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
```

---

## Backend Development

### Setup Backend

Navigate to the `backend` directory and install the package with development dependencies in editable mode:

```bash
cd backend
python -m pip install -e ".[dev]"
```

### Running Backend Server

Start the FastAPI application with Uvicorn:

```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Once running, interactive API documentation is available at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## Evaluation Core & CLI Usage

### Running Evaluation Pipeline via CLI

Phase 2 includes a real evaluation execution pipeline using `MockTargetAdapter` and `ExactMatchEvaluator`:

```bash
probenest evaluate --dataset ../datasets/golden/example.json
```

Output format:

```text
PROBENEST EVALUATION

Target: default
Dataset: datasets/golden/example.json

Run: run_86abebd0
Status: COMPLETED
Cases: 5
Passed: 4
Failed: 1

Results:
  PASS qa_001 (ExactMatchEvaluator): Actual output exactly matches expected output.
  PASS qa_002 (ExactMatchEvaluator): Actual output exactly matches expected output.
  FAIL qa_003_fail (ExactMatchEvaluator): Mismatch...
  PASS qa_004 (ExactMatchEvaluator): Actual output exactly matches expected output.
  PASS qa_005 (ExactMatchEvaluator): Actual output exactly matches expected output.
```

---

## Evaluation API Endpoints

- `POST /api/v1/evaluations` — Trigger a new evaluation run
- `GET /api/v1/evaluations` — List historical evaluation runs
- `GET /api/v1/evaluations/{run_id}` — Retrieve detailed evaluation run and case outcomes

---

## Frontend Development

### Setup Frontend

Navigate to the `frontend` directory and install Node dependencies:

```bash
cd frontend
npm install
```

### Running Frontend Development Server

Start Vite dev server:

```bash
cd frontend
npm run dev
```

The frontend application will run at `http://localhost:5173`. It connects to the FastAPI backend at `http://127.0.0.1:8000` via the configured Vite proxy.

---

## Testing & Linting

### Backend Tests

Run unit tests using Pytest:

```bash
cd backend
python -m pytest
```

### Backend Linting

Run static lint checks with Ruff:

```bash
cd backend
python -m ruff check .
```

### Frontend Build

Verify TypeScript compilation and Vite build:

```bash
cd frontend
npm run build
```
