from typer.testing import CliRunner

from app.cli import app

runner = CliRunner()


def test_cli_evaluate_quality_command() -> None:
    """Test probenest evaluate --evaluators quality command execution."""
    result = runner.invoke(app, ["evaluate", "--target", "mock", "--evaluators", "quality"])
    assert result.exit_code == 0
    assert "PROBENEST QUALITY EVALUATION" in result.output
    assert "Accuracy" in result.output
    assert "Relevance" in result.output
    assert "Faithfulness" in result.output
    assert "Hallucination" in result.output
