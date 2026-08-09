import pytest

from app.judges.base import EvaluationJudgeError
from app.judges.factory import get_judge
from app.judges.mock import MockEvaluationJudge
from app.judges.ollama import OllamaEvaluationJudge


def test_mock_evaluation_judge() -> None:
    """Test MockEvaluationJudge output for accuracy, relevance, faithfulness, and hallucination."""
    judge = MockEvaluationJudge()

    acc_res = judge.judge("accuracy", "What is 2+2?", None, "4", "4")
    assert acc_res.score == 1.0

    rel_res = judge.judge("relevance", "What is the return policy?", None, None, "Returns allowed in 30 days")
    assert rel_res.score == 1.0

    faith_res = judge.judge("faithfulness", "What is return period?", ["Refunds in 30 days."], None, "Refunds in 30 days.")
    assert faith_res.score == 1.0

    halluc_res = judge.judge("hallucination", "What is return period?", ["Refunds in 30 days."], None, "Refunds in 30 days.")
    assert halluc_res.score == 1.0


def test_ollama_judge_offline_error() -> None:
    """Test OllamaEvaluationJudge raises EvaluationJudgeError when service is offline."""
    judge = OllamaEvaluationJudge(base_url="http://127.0.0.1:59999")
    with pytest.raises(EvaluationJudgeError, match="Ollama evaluation judge unavailable"):
        judge.judge("accuracy", "prompt", None, "expected", "actual")


def test_judge_factory() -> None:
    """Test get_judge factory returns MockEvaluationJudge by default."""
    judge = get_judge("mock")
    assert isinstance(judge, MockEvaluationJudge)
