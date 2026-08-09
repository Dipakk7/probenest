from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, Field

from app.domain.case import EvaluationCase


class TargetResponse(BaseModel):
    """Response returned by a target application adapter."""

    output: str = Field(description="Generated output text from the target")
    context: list[str] | None = Field(default=None, description="Retrieved context snippets used by the target")
    tool_calls: list[dict[str, Any]] | None = Field(default=None, description="Tool calls executed during response generation")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Execution metadata (e.g. latency, model name)")


@runtime_checkable
class TargetAdapter(Protocol):
    """Interface protocol for target AI applications."""

    def run(self, case: EvaluationCase) -> TargetResponse:
        """Execute evaluation case against the target application and return TargetResponse."""
        ...
