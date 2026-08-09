from app.domain.case import EvaluationCase
from app.domain.evaluator import EvaluationResult
from app.domain.target import TargetResponse
from app.judges.base import EvaluationJudge
from app.judges.factory import get_judge


class HallucinationEvaluator:
    """Evaluates hallucination risk / grounding of target output against retrieved context."""

    name: str = "HallucinationEvaluator"

    def __init__(self, judge: EvaluationJudge | None = None) -> None:
        self.judge = judge or get_judge()

    def evaluate(self, case: EvaluationCase, response: TargetResponse) -> EvaluationResult:
        """Evaluate response hallucination score (1.0 = fully grounded, 0.0 = severe hallucination)."""
        context = response.context or []

        judge_res = self.judge.judge(
            task_type="hallucination",
            prompt=case.input,
            context=context,
            expected_output=case.expected_output,
            actual_output=response.output,
        )

        # Score: 1.0 means no hallucination / pass
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
                "grounding_score": judge_res.score,
            },
        )
