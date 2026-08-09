from app.domain.case import EvaluationCase
from app.domain.evaluator import EvaluationResult
from app.domain.run import EvaluationRun, RunStatus
from app.domain.target import TargetResponse


def test_evaluation_case_creation() -> None:
    """Test valid EvaluationCase model instantiation."""
    case = EvaluationCase(
        id="case_001",
        input="Hello world",
        expected_output="Hello world response",
        category="quality",
        tags=["smoke"],
    )
    assert case.id == "case_001"
    assert case.input == "Hello world"
    assert case.expected_output == "Hello world response"
    assert case.category == "quality"
    assert "smoke" in case.tags


def test_target_response_creation() -> None:
    """Test valid TargetResponse instantiation."""
    res = TargetResponse(output="Sample output", metadata={"tokens": 10})
    assert res.output == "Sample output"
    assert res.metadata["tokens"] == 10


def test_evaluation_result_creation() -> None:
    """Test valid EvaluationResult instantiation."""
    result = EvaluationResult(
        test_id="case_001",
        evaluator="ExactMatchEvaluator",
        passed=True,
        score=1.0,
        reason="Match success",
    )
    assert result.passed is True
    assert result.score == 1.0


def test_evaluation_run_creation() -> None:
    """Test valid EvaluationRun instantiation."""
    run = EvaluationRun(run_id="run_123", status=RunStatus.COMPLETED)
    assert run.run_id == "run_123"
    assert run.status == RunStatus.COMPLETED
