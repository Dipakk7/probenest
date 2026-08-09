from typer.testing import CliRunner

from app.cli import app

runner = CliRunner()


def test_cli_report_command(tmp_path) -> None:
    """Test probenest report CLI command execution and file output."""
    eval_res = runner.invoke(app, ["evaluate", "--target", "mock"])
    assert eval_res.exit_code == 0
    run_id = eval_res.output.split("Run: ")[1].split("\n")[0].strip()

    # Test probenest report
    report_res = runner.invoke(app, ["report", run_id])
    assert report_res.exit_code == 0
    assert "PROBENEST REPORT GENERATION" in report_res.output

    # Test probenest report with custom output
    out_file = tmp_path / "custom_report.json"
    out_res = runner.invoke(app, ["report", run_id, "--output", str(out_file)])
    assert out_res.exit_code == 0
    assert out_file.is_file()


def test_cli_exit_codes() -> None:
    """Test standardized CLI exit codes: 0=success, 2=invalid args."""
    # Invalid dataset path -> Exit Code 2
    res_bad = runner.invoke(app, ["evaluate", "--dataset", "nonexistent.json"])
    assert res_bad.exit_code == 2

    # Nonexistent run score -> Exit Code 2
    res_bad_run = runner.invoke(app, ["score", "nonexistent_run_id"])
    assert res_bad_run.exit_code == 2
