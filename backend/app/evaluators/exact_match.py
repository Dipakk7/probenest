from app.domain.case import EvaluationCase
from app.domain.evaluator import EvaluationResult
from app.domain.target import TargetResponse


class ExactMatchEvaluator:
    """Deterministic demonstration evaluator asserting exact text match between target response and expected output."""

    name: str = "ExactMatchEvaluator"

    def evaluate(self, case: EvaluationCase, response: TargetResponse) -> EvaluationResult:
        """Compare response output with expected case output."""
        if case.expected_output is None:
            return EvaluationResult(
                test_id=case.id,
                evaluator=self.name,
                passed=True,
                score=1.0,
                reason="No expected output specified; default pass.",
                evidence={"actual_output": response.output},
            )

        actual_norm = response.output.strip()
        expected_norm = case.expected_output.strip()

        passed = actual_norm == expected_norm
        score = 1.0 if passed else 0.0

        if passed:
            reason = "Actual output exactly matches expected output."
        else:
            reason = f"Mismatch: expected '{expected_norm}' but received '{actual_norm}'."

        return EvaluationResult(
            test_id=case.id,
            evaluator=self.name,
            passed=passed,
            score=score,
            reason=reason,
            evidence={
                "actual_output": response.output,
                "expected_output": case.expected_output,
            },
        )
