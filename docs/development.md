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

## Running Quality & Red-Team Evaluations

### Quality Evaluation CLI

```bash
probenest evaluate --target mock --evaluators quality
probenest evaluate --target demorrag --dataset datasets/golden/rag.json --evaluators quality
```

### Red-Team Evaluation CLI

Run automated adversarial attack suites:

```bash
# Run all red-team suites against mock target
probenest redteam --target mock

# Run prompt injection suite against DemoRAG
probenest redteam --target demorrag --category prompt_injection

# Run custom attack dataset
probenest redteam --target demorrag --dataset datasets/redteam/injection.json
```

Output format:

```text
PROBENEST RED-TEAM EVALUATION

Target: demorrag

Prompt Injection
  5/5 defended
  0 failures

Instruction Override
  3/3 defended
  0 failures

Jailbreak
  8/8 defended
  0 failures

Data Leakage
  8/8 defended
  0 failures

Tool Abuse
  8/8 defended
  0 failures

TOTAL TESTS: 32
FAILURES: 0
High-risk failures: 0
```

---

## API Usage

Trigger red-team evaluation via REST API:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/redteam \
  -H "Content-Type: application/json" \
  -d '{"target": "demorrag", "category": "prompt_injection"}'
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
