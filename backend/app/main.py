from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import evaluations_router, redteam_router, scoring_router
from app.core.config import settings
from app.core.logging import logger
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """FastAPI application lifespan manager initializing SQLite database."""
    logger.info("Initializing database metadata foundation...")
    init_db()
    logger.info("Probenest backend startup complete.")
    yield
    logger.info("Probenest backend shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Probenest — Adversarial AI Evaluation & Reliability Platform API",
    lifespan=lifespan,
)

# Configure CORS for local React frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(evaluations_router, prefix="/api/v1", tags=["evaluations"])
app.include_router(redteam_router, prefix="/api/v1", tags=["redteam"])
app.include_router(scoring_router, prefix="/api/v1", tags=["scoring"])


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Health check endpoint confirming FastAPI backend operational status."""
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV}


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    """Root endpoint welcoming API clients."""
    return {"message": "Welcome to Probenest API", "docs": "/docs"}
