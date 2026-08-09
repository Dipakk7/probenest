from typer.testing import CliRunner

from app.cli import app

runner = CliRunner()


def test_cli_score_and_compare_commands() -> None:
    """Test probenest score and probenest compare CLI execution."""
    eval_res1 = runner.invoke(app, ["evaluate", "--target", "mock"])
    assert eval_res1.exit_code == 0
    run_id1 = eval_res1.output.split("Run: ")[1].split("\n")[0].strip()

    eval_res2 = runner.invoke(app, ["evaluate", "--target", "mock"])
    assert eval_res2.exit_code == 0
    run_id2 = eval_res2.output.split("Run: ")[1].split("\n")[0].strip()

    # Test probenest score
    score_res = runner.invoke(app, ["score", run_id1])
    assert score_res.exit_code == 0
    assert "PROBENEST RUN SCORE SUMMARY" in score_res.output
    assert "QUALITY SCORE" in score_res.output

    # Test probenest compare
    comp_res = runner.invoke(app, ["compare", run_id1, run_id2])
    assert comp_res.exit_code == 0
    assert "PROBENEST RUN COMPARISON" in comp_res.output
    assert "Baseline:" in comp_res.output
    assert "Candidate:" in comp_res.output
