from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(default="ok", description="Service status indicator")
    service: str = Field(default="probenest", description="Service name")


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Return health status of Probenest backend service."""
    return HealthResponse(status="ok", service="probenest")
