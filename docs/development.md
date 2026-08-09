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

## Running Quality Evaluations

### CLI Execution

Run the Quality Evaluation Engine across Accuracy, Relevance, Faithfulness, and Hallucination metrics:

```bash
# Evaluate mock target
probenest evaluate --target mock --evaluators quality

# Evaluate DemoRAG target (with DemoRAG server running on port 8001)
probenest evaluate --target demorrag --dataset ../datasets/golden/rag.json --evaluators quality
```

Output format:

```text
PROBENEST QUALITY EVALUATION

Target: demorrag
Dataset: datasets/golden/rag.json

Run: run_fe0d9622
Status: COMPLETED
Cases: 10

Accuracy
  4/10 passed
  Score: 0.40

Relevance
  10/10 passed
  Score: 1.00

Faithfulness
  10/10 passed
  Score: 1.00

Hallucination
  8/10 passed
  Score: 0.80
```

---

## API Usage

Trigger quality evaluation via REST API:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/evaluations \
  -H "Content-Type: application/json" \
  -d '{"target": "demorrag", "evaluators": ["accuracy", "relevance", "faithfulness", "hallucination"]}'
```

---

## Testing & Quality

```bash
# Run backend tests
cd backend && python -m pytest && python -m ruff check .

# Run DemoRAG tests
cd demo_target/demo_rag && python -m pytest && python -m ruff check .

# Run frontend build
cd frontend && npm run build
```
