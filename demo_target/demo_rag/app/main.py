from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status

from app.config import settings
from app.llm.base import LLMProviderError
from app.models import QueryRequest, QueryResponse
from app.rag.pipeline import RAGPipeline

rag_pipeline: RAGPipeline | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan manager initializing DemoRAG pipeline."""
    global rag_pipeline
    rag_pipeline = RAGPipeline()
    yield


app = FastAPI(
    title="DemoRAG",
    version="0.1.0",
    description="Fictional Reference RAG Target Application for Probenest Evaluation",
    lifespan=lifespan,
)


@app.get("/", tags=["root"])
def read_root() -> dict[str, str]:
    """Root endpoint identifying DemoRAG."""
    return {
        "service": "DemoRAG",
        "status": "running",
        "llm_provider": settings.LLM_PROVIDER,
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": "demorag"}


@app.post("/query", response_model=QueryResponse, tags=["query"])
def query_endpoint(payload: QueryRequest) -> QueryResponse:
    """Execute RAG query pipeline for user question."""
    global rag_pipeline
    if rag_pipeline is None:
        rag_pipeline = RAGPipeline()

    try:
        return rag_pipeline.query(payload.question)
    except LLMProviderError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG query execution failed: {e}",
        ) from e


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.DEMORAG_HOST,
        port=settings.DEMORAG_PORT,
        reload=True,
    )
