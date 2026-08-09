from app.domain.evaluator import Evaluator
from app.evaluators.accuracy import AccuracyEvaluator
from app.evaluators.exact_match import ExactMatchEvaluator
from app.evaluators.faithfulness import FaithfulnessEvaluator
from app.evaluators.hallucination import HallucinationEvaluator
from app.evaluators.relevance import RelevanceEvaluator
from app.judges.base import EvaluationJudge


def get_evaluators_by_names(names: list[str] | None = None, judge: EvaluationJudge | None = None) -> list[Evaluator]:
    """Resolve metric names to a list of Evaluator instances.

    Supported names: 'exact_match', 'accuracy', 'relevance', 'faithfulness', 'hallucination', 'quality', 'all'.
    """
    if not names:
        # Default quality suite if none provided or empty
        return [
            AccuracyEvaluator(judge=judge),
            RelevanceEvaluator(judge=judge),
            FaithfulnessEvaluator(judge=judge),
            HallucinationEvaluator(judge=judge),
        ]

    normalized_names = [n.lower().strip() for n in names]
    evaluators: list[Evaluator] = []

    for name in normalized_names:
        if name in ["exact_match", "exactmatch"]:
            evaluators.append(ExactMatchEvaluator())
        elif name in ["accuracy", "acc"]:
            evaluators.append(AccuracyEvaluator(judge=judge))
        elif name in ["relevance", "rel"]:
            evaluators.append(RelevanceEvaluator(judge=judge))
        elif name in ["faithfulness", "faith"]:
            evaluators.append(FaithfulnessEvaluator(judge=judge))
        elif name in ["hallucination", "halluc"]:
            evaluators.append(HallucinationEvaluator(judge=judge))
        elif name in ["quality", "all"]:
            evaluators.extend([
                AccuracyEvaluator(judge=judge),
                RelevanceEvaluator(judge=judge),
                FaithfulnessEvaluator(judge=judge),
                HallucinationEvaluator(judge=judge),
            ])

    # Default fallback
    if not evaluators:
        evaluators = [AccuracyEvaluator(judge=judge)]

    return evaluators
