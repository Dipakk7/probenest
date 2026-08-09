from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, Field

from app.domain.case import EvaluationCase
from app.domain.target import TargetResponse


class EvaluationResult(BaseModel):
    """Standardized result of evaluating a single case with a specific evaluator."""

    test_id: str = Field(description="ID of the evaluation case")
    evaluator: str = Field(description="Name of the evaluator")
    passed: bool = Field(description="Pass/Fail status indicator")
    score: float = Field(description="Numerical evaluation score (0.0 to 1.0)")
    reason: str = Field(description="Human-readable explanation of evaluation outcome")
    severity: str | None = Field(default=None, description="Severity level for security/quality failures")
    evidence: dict[str, Any] = Field(default_factory=dict, description="Detailed evidence payload supporting the result")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional result metadata")


@runtime_checkable
class Evaluator(Protocol):
    """Interface protocol for evaluation metrics and probes."""

    name: str

    def evaluate(self, case: EvaluationCase, response: TargetResponse) -> EvaluationResult:
        """Evaluate case and target response, returning EvaluationResult."""
        ...
