from typing import Any

from pydantic import BaseModel, Field


class EvaluationCase(BaseModel):
    """Represents a single test case for evaluation."""

    id: str = Field(description="Unique case identifier")
    input: str = Field(description="Input query or prompt sent to the target")
    expected_output: str | None = Field(default=None, description="Expected response output")
    expected_context: list[str] | None = Field(default=None, description="Expected retrieved context snippets")
    expected_tool_calls: list[dict[str, Any]] | None = Field(default=None, description="Expected tool call signatures")
    category: str | None = Field(default=None, description="Functional or vulnerability category")
    tags: list[str] = Field(default_factory=list, description="Categorical tags for filtering")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary case metadata")
