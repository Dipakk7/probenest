.PHONY: help setup dev-backend dev-frontend test lint build clean

help:
	@echo "Probenest Development Commands:"
	@echo "  make setup         Install backend and frontend dependencies"
	@echo "  make dev-backend   Run FastAPI backend development server"
	@echo "  make dev-frontend  Run React Vite frontend development server"
	@echo "  make test          Run backend test suite"
	@echo "  make lint          Run Ruff linter on backend"
	@echo "  make build         Build frontend production assets"

setup:
	cd backend && python -m pip install -e .
	cd frontend && npm install

dev-backend:
	cd backend && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

dev-frontend:
	cd frontend && npm run dev

test:
	cd backend && pytest

lint:
	cd backend && ruff check .

build:
	cd frontend && npm run build

clean:
	rm -rf backend/*.db backend/build backend/*.egg-info frontend/dist
