from app.domain.case import EvaluationCase
from app.domain.target import TargetResponse
from app.evaluators.accuracy import AccuracyEvaluator
from app.evaluators.faithfulness import FaithfulnessEvaluator
from app.evaluators.hallucination import HallucinationEvaluator
from app.evaluators.relevance import RelevanceEvaluator
from app.judges.mock import MockEvaluationJudge


def test_accuracy_evaluator() -> None:
    """Test AccuracyEvaluator exact match and judge fallback."""
    judge = MockEvaluationJudge()
    evaluator = AccuracyEvaluator(judge=judge)

    case = EvaluationCase(id="c1", input="What is refund period?", expected_output="30 days")
    res_pass = TargetResponse(output="30 days")
    res_fail = TargetResponse(output="Incorrect response")

    result1 = evaluator.evaluate(case, res_pass)
    assert result1.passed is True
    assert result1.score == 1.0

    result2 = evaluator.evaluate(case, res_fail)
    assert result2.passed is False
    assert result2.score == 0.0


def test_relevance_evaluator() -> None:
    """Test RelevanceEvaluator."""
    judge = MockEvaluationJudge()
    evaluator = RelevanceEvaluator(judge=judge)

    case = EvaluationCase(id="c2", input="Where is headquarters?")
    response = TargetResponse(output="Probenest headquarters is located in San Francisco.")

    result = evaluator.evaluate(case, response)
    assert result.passed is True
    assert result.score == 1.0


def test_faithfulness_evaluator() -> None:
    """Test FaithfulnessEvaluator."""
    judge = MockEvaluationJudge()
    evaluator = FaithfulnessEvaluator(judge=judge)

    case = EvaluationCase(id="c3", input="What is refund period?")
    response = TargetResponse(output="Refunds in 30 days.", context=["Refunds are allowed within 30 days."])

    result = evaluator.evaluate(case, response)
    assert result.passed is True
    assert result.score == 1.0


def test_hallucination_evaluator() -> None:
    """Test HallucinationEvaluator."""
    judge = MockEvaluationJudge()
    evaluator = HallucinationEvaluator(judge=judge)

    case = EvaluationCase(id="c4", input="What is refund period?")
    response = TargetResponse(output="Refunds in 30 days.", context=["Refunds are allowed within 30 days."])

    result = evaluator.evaluate(case, response)
    assert result.passed is True
    assert result.score == 1.0
