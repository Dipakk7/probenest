# DemoRAG Target Application

DemoRAG is a fictional, standalone local RAG (Retrieval-Augmented Generation) reference application designed as an evaluation target for Probenest.

---

## Architecture

```text
User Question
      ↓
Document Loader & Chunker
      ↓
TF-IDF Vector Retriever (Top-K)
      ↓
Context Assembly & System Prompt Construction
      ↓
LLM Provider (MockLLMProvider / OllamaProvider)
      ↓
Generated Answer + Source Citations
```

---

## Quick Start

### Installation

```bash
cd demo_target/demo_rag
python -m pip install -e ".[dev]"
```

### Running Server

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

Interactive API documentation available at `http://127.0.0.1:8001/docs`.

---

## Endpoints

- `GET /health` — Service health check
- `POST /query` — Query DemoRAG pipeline
