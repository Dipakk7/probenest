from typer.testing import CliRunner

from app.cli import app

runner = CliRunner()


def test_cli_redteam_command() -> None:
    """Test probenest redteam CLI command execution."""
    result = runner.invoke(app, ["redteam", "--target", "mock"])
    assert result.exit_code == 0
    assert "PROBENEST RED-TEAM EVALUATION" in result.output
    assert "TOTAL TESTS:" in result.output
    assert "FAILURES:" in result.output
