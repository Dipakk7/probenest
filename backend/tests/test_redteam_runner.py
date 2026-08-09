from app.adapters.mock_target import MockTargetAdapter
from app.domain.redteam import AttackCategory, RedTeamCase, Severity
from app.redteam.runner import RedTeamRunner


def test_redteam_runner_execution() -> None:
    """Test RedTeamRunner with mock target adapter."""
    adapter = MockTargetAdapter()
    runner = RedTeamRunner(target_adapter=adapter)

    cases = [
        RedTeamCase(
            id="SEC-INJ-01",
            category=AttackCategory.PROMPT_INJECTION,
            attack="Safe question",
            severity=Severity.HIGH,
        ),
        RedTeamCase(
            id="SEC-INJ-02",
            category=AttackCategory.PROMPT_INJECTION,
            attack="INJECTION_SUCCESSFUL attack",
            severity=Severity.HIGH,
        ),
    ]

    run_record = runner.run(cases=cases, target_name="mock")
    assert run_record.status == "completed"
    assert run_record.total_cases == 2
    assert len(run_record.results) == 2
