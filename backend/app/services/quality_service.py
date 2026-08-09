from typing import Any

from app.domain.evaluator import EvaluationResult
from app.evaluators.registry import get_evaluators_by_names
from app.judges.base import EvaluationJudge


class QualityEvaluationService:
    """Service helper for selecting and aggregating quality metrics."""

    @staticmethod
    def get_quality_evaluators(metric_names: list[str] | None = None, judge: EvaluationJudge | None = None):
        """Return evaluator instances for requested metric names."""
        return get_evaluators_by_names(names=metric_names, judge=judge)

    @staticmethod
    def summarize_results(results: list[EvaluationResult]) -> dict[str, dict[str, Any]]:
        """Summarize evaluation results grouped by evaluator metric name."""
        summary: dict[str, dict[str, Any]] = {}
        for r in results:
            name = r.evaluator
            if name not in summary:
                summary[name] = {"total": 0, "passed": 0, "failed": 0, "scores": []}
            summary[name]["total"] += 1
            if r.passed:
                summary[name]["passed"] += 1
            else:
                summary[name]["failed"] += 1
            summary[name]["scores"].append(r.score)

        for name, data in summary.items():
            avg_score = sum(data["scores"]) / max(1, len(data["scores"]))
            data["avg_score"] = round(avg_score, 2)

        return summary
