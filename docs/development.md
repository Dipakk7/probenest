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

Navigate to the `backend` directory and install the package in editable mode:

```bash
cd backend
python -m pip install -e .
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

### CLI Usage

The `probenest` command is installed in your Python environment:

```bash
probenest --help
probenest evaluate --help
probenest redteam --help
probenest compare --help
```

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
pytest
```

### Backend Linting

Run static lint checks with Ruff:

```bash
cd backend
ruff check .
```

### Frontend Build

Verify TypeScript compilation and Vite build:

```bash
cd frontend
npm run build
```
