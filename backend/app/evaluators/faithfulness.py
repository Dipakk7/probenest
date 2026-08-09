from app.domain.case import EvaluationCase
from app.domain.evaluator import EvaluationResult
from app.domain.target import TargetResponse
from app.judges.base import EvaluationJudge
from app.judges.factory import get_judge


class FaithfulnessEvaluator:
    """Evaluates whether claims in target output are supported by retrieved context."""

    name: str = "FaithfulnessEvaluator"

    def __init__(self, judge: EvaluationJudge | None = None) -> None:
        self.judge = judge or get_judge()

    def evaluate(self, case: EvaluationCase, response: TargetResponse) -> EvaluationResult:
        """Evaluate response faithfulness to retrieved context."""
        context = response.context or []

        judge_res = self.judge.judge(
            task_type="faithfulness",
            prompt=case.input,
            context=context,
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
                "context_snippets_count": len(context),
                "judge_score": judge_res.score,
            },
        )
