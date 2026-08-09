from app.adapters.mock_target import MockTargetAdapter
from app.domain.case import EvaluationCase
from app.domain.run import RunStatus
from app.evaluators.exact_match import ExactMatchEvaluator
from app.runner.runner import EvaluationRunner


def test_runner_execution_success_and_failure() -> None:
    """Test runner execution with pass and fail cases using MockTargetAdapter and ExactMatchEvaluator."""
    cases = [
        EvaluationCase(id="c1", input="What is 2+2?", expected_output="4"),
        EvaluationCase(id="c2_fail", input="What is the capital of France?", expected_output="Paris"),
    ]

    adapter = MockTargetAdapter()
    evaluator = ExactMatchEvaluator()
    runner = EvaluationRunner(target_adapter=adapter, evaluators=[evaluator])

    run_record = runner.run(cases=cases, run_id="test_run_001")

    assert run_record.run_id == "test_run_001"
    assert run_record.status == RunStatus.COMPLETED
    assert run_record.total_cases == 2
    assert run_record.passed_cases == 1
    assert run_record.failed_cases == 1
    assert len(run_record.results) == 2
    assert run_record.results[0].passed is True
    assert run_record.results[1].passed is False
