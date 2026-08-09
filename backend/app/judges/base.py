from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field


class JudgeResult(BaseModel):
    """Structured result returned by an evaluation judge."""

    score: float = Field(description="Numerical evaluation score (0.0 to 1.0)")
    reason: str = Field(description="Human-readable justification of evaluation score")


class EvaluationJudgeError(Exception):
    """Exception raised when an evaluation judge fails."""


@runtime_checkable
class EvaluationJudge(Protocol):
    """Interface protocol for evaluation judges evaluating AI output quality."""

    def judge(
        self,
        task_type: str,
        prompt: str,
        context: list[str] | None,
        expected_output: str | None,
        actual_output: str,
    ) -> JudgeResult:
        """Evaluate actual output against prompt, context, or expected output."""
        ...
