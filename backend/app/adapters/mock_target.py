from typing import Any

from app.domain.case import EvaluationCase
from app.domain.target import TargetResponse


class MockTargetAdapter:
    """Deterministic mock target application adapter for engine testing."""

    def __init__(self, default_response: str | None = None, overrides: dict[str, str] | None = None) -> None:
        self.default_response = default_response
        self.overrides = overrides or {}

    def run(self, case: EvaluationCase) -> TargetResponse:
        """Deterministically generate a TargetResponse based on the evaluation case input."""
        # 1. Check explicit mock overrides for this case ID or input
        if case.id in self.overrides:
            output = self.overrides[case.id]
        elif case.input in self.overrides:
            output = self.overrides[case.input]
        elif self.default_response is not None:
            output = self.default_response
        elif case.expected_output is not None:
            # If case ID signals deliberate failure for testing, manipulate response
            if "fail" in case.id.lower():
                output = f"Incorrect response for {case.input}"
            else:
                output = case.expected_output
        else:
            output = f"Echo: {case.input}"

        metadata: dict[str, Any] = {
            "adapter": "MockTargetAdapter",
            "simulated_latency_ms": 5,
        }

        return TargetResponse(
            output=output,
            context=case.expected_context,
            tool_calls=case.expected_tool_calls,
            metadata=metadata,
        )
