from app.domain.case import EvaluationCase
from app.domain.evaluator import EvaluationResult
from app.domain.target import TargetResponse
from app.judges.base import EvaluationJudge
from app.judges.factory import get_judge


class RelevanceEvaluator:
    """Evaluates whether the target output directly addresses the user question."""

    name: str = "RelevanceEvaluator"

    def __init__(self, judge: EvaluationJudge | None = None) -> None:
        self.judge = judge or get_judge()

    def evaluate(self, case: EvaluationCase, response: TargetResponse) -> EvaluationResult:
        """Evaluate query response relevance."""
        if not response.output.strip():
            return EvaluationResult(
                test_id=case.id,
                evaluator=self.name,
                passed=False,
                score=0.0,
                reason="Target output is completely empty.",
                evidence={"prompt": case.input},
            )

        judge_res = self.judge.judge(
            task_type="relevance",
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
                "prompt": case.input,
                "actual_output": response.output,
                "judge_score": judge_res.score,
            },
        )
