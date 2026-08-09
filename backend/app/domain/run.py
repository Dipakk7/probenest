from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field

from app.domain.evaluator import EvaluationResult


class RunStatus(str, Enum):
    """Possible statuses for an evaluation run."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EvaluationRun(BaseModel):
    """Represents a complete evaluation run containing aggregate metrics and case results."""

    run_id: str = Field(description="Unique evaluation run identifier")
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Run start timestamp")
    completed_at: datetime | None = Field(default=None, description="Run completion timestamp")
    status: RunStatus = Field(default=RunStatus.PENDING, description="Execution status")
    total_cases: int = Field(default=0, description="Total cases evaluated")
    passed_cases: int = Field(default=0, description="Total passed cases")
    failed_cases: int = Field(default=0, description="Total failed cases")
    results: list[EvaluationResult] = Field(default_factory=list, description="Individual case evaluation results")
