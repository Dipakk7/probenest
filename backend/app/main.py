from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.api.routes.health import HealthResponse, get_health
from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager initializing logging and database metadata."""
    setup_logging()
    logger.info(f"Starting {settings.APP_NAME} in [{settings.APP_ENV}] mode...")
    init_db()
    yield
    logger.info(f"Shutting down {settings.APP_NAME}...")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Adversarial AI Evaluation & Reliability Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/", tags=["root"])
def read_root() -> dict[str, str]:
    """Root endpoint identifying Probenest."""
    return {
        "service": settings.APP_NAME,
        "status": "running",
        "description": "Adversarial AI Evaluation & Reliability Platform",
        "docs": "/docs"
    }


# Health endpoint exposed directly at /health
@app.get("/health", response_model=HealthResponse, tags=["health"])
def health_endpoint() -> HealthResponse:
    """Health check endpoint."""
    return get_health()


# Include API router
app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
