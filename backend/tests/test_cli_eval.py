from typer.testing import CliRunner

from app.cli import app

runner = CliRunner()


def test_cli_evaluate_command() -> None:
    """Test probenest evaluate CLI command execution."""
    result = runner.invoke(app, ["evaluate"])
    assert result.exit_code == 0
    assert "PROBENEST EVALUATION" in result.output
    assert "Passed: 4" in result.output
    assert "Failed: 1" in result.output
    assert "PASS qa_001" in result.output
    assert "FAIL qa_003_fail" in result.output
