from app.domain.case import EvaluationCase
from app.domain.evaluator import EvaluationResult
from app.domain.target import TargetResponse
from app.judges.base import EvaluationJudge
from app.judges.factory import get_judge


class AccuracyEvaluator:
    """Evaluates semantic accuracy comparing actual target output against expected ground truth."""

    name: str = "AccuracyEvaluator"

    def __init__(self, judge: EvaluationJudge | None = None) -> None:
        self.judge = judge or get_judge()

    def evaluate(self, case: EvaluationCase, response: TargetResponse) -> EvaluationResult:
        """Evaluate response accuracy."""
        if not case.expected_output:
            return EvaluationResult(
                test_id=case.id,
                evaluator=self.name,
                passed=True,
                score=1.0,
                reason="No expected ground truth output specified; default pass.",
                evidence={"actual_output": response.output},
            )

        actual_norm = response.output.strip()
        expected_norm = case.expected_output.strip()

        # Layer 1 & 2: Deterministic exact/substring match
        if actual_norm.lower() == expected_norm.lower():
            return EvaluationResult(
                test_id=case.id,
                evaluator=self.name,
                passed=True,
                score=1.0,
                reason="Actual output exactly matches expected output.",
                evidence={"actual_output": response.output, "expected_output": case.expected_output},
            )

        if expected_norm.lower() in actual_norm.lower():
            return EvaluationResult(
                test_id=case.id,
                evaluator=self.name,
                passed=True,
                score=1.0,
                reason="Actual output contains expected ground truth facts.",
                evidence={"actual_output": response.output, "expected_output": case.expected_output},
            )

        # Layer 3: Semantic evaluation judge
        judge_res = self.judge.judge(
            task_type="accuracy",
            prompt=case.input,
            context=response.context,
            expected_output=case.expected_output,
            actual_output=response.output,
        )

        passed = judge_res.score >= 0.7

        return EvaluationResult(
            test_id=case.id,
            evaluator=self.name,
            passed=passed,
            score=judge_res.score,
            reason=judge_res.reason,
            evidence={
                "actual_output": response.output,
                "expected_output": case.expected_output,
                "judge_score": judge_res.score,
            },
        )
