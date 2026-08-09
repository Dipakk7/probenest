import json
from pathlib import Path

import typer

from app.adapters.demo_rag import DemoRAGAdapter
from app.adapters.mock_target import MockTargetAdapter
from app.db.database import SessionLocal, init_db
from app.domain.redteam import RedTeamCase
from app.evaluators.registry import get_evaluators_by_names
from app.loaders.dataset import DatasetLoadError
from app.loaders.redteam_loader import RedTeamDatasetLoader
from app.regression.engine import RegressionEngine
from app.repositories.evaluation_repository import EvaluationRepository
from app.repositories.redteam_repository import RedTeamRepository
from app.repositories.score_repository import ScoreRepository
from app.scoring.engine import ScoreEngine
from app.services.evaluation_service import EvaluationService
from app.services.quality_service import QualityEvaluationService
from app.services.redteam_service import RedTeamService

app = typer.Typer(
    name="probenest",
    help="Probenest — Adversarial AI Evaluation & Reliability Platform CLI",
    add_completion=False,
)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Probenest CLI root command."""
    if ctx.invoked_subcommand is None:
        typer.echo("Probenest CLI v0.1.0")
        typer.echo("Run 'probenest --help' to view available commands.")


@app.command("evaluate")
def evaluate(
    target: str = typer.Option("mock", "--target", "-t", help="Target AI application identifier ('mock' or 'demorrag')"),
    dataset: str | None = typer.Option(
        None,
        "--dataset",
        "-d",
        help="Evaluation dataset JSON file path",
    ),
    evaluators: str = typer.Option(
        "quality",
        "--evaluators",
        "-e",
        help="Comma-separated list of evaluators (accuracy, relevance, faithfulness, hallucination, exact_match, quality)",
    ),
    debug: bool = typer.Option(False, "--debug", help="Enable verbose debug output and tracebacks"),
) -> None:
    """Run AI quality evaluation pipeline against target application."""
    target_key = target.lower()
    if target_key in ["demorrag", "rag"]:
        target_adapter = DemoRAGAdapter()
        default_dataset_rel = "rag.json"
    else:
        target_adapter = MockTargetAdapter()
        default_dataset_rel = "example.json"

    if dataset:
        dataset_path = Path(dataset)
    else:
        repo_root = Path(__file__).resolve().parents[2]
        dataset_path = repo_root / "datasets" / "golden" / default_dataset_rel
        if not dataset_path.is_file():
            dataset_path = Path(f"datasets/golden/{default_dataset_rel}").resolve()

    evaluator_names = [e.strip() for e in evaluators.split(",") if e.strip()]
    evaluator_instances = get_evaluators_by_names(evaluator_names)

    typer.echo("PROBENEST QUALITY EVALUATION\n")
    typer.echo(f"Target: {target}")
    typer.echo(f"Dataset: {dataset_path}\n")

    init_db()
    db = SessionLocal()
    try:
        service = EvaluationService(db)
        run_record = service.run_evaluation(
            dataset_path_or_cases=dataset_path,
            target_adapter=target_adapter,
            evaluators=evaluator_instances,
            target_name=target,
        )

        typer.echo(f"Run: {run_record.run_id}")
        typer.echo(f"Status: {run_record.status.value.upper()}")
        typer.echo(f"Cases: {run_record.total_cases}\n")

        # Display metric summaries
        summaries = QualityEvaluationService.summarize_results(run_record.results)
        for metric_name, summary in summaries.items():
            short_name = metric_name.replace("Evaluator", "")
            typer.echo(typer.style(short_name, bold=True))
            passed = summary["passed"]
            total = summary["total"]
            avg_score = summary["avg_score"]

            color = typer.colors.GREEN if avg_score >= 0.7 else typer.colors.RED
            formatted_stats = typer.style(f"  {passed}/{total} passed\n  Score: {avg_score:.2f}\n", fg=color)
            typer.echo(formatted_stats)

    except DatasetLoadError as e:
        typer.echo(typer.style(f"Dataset Error: {e}", fg=typer.colors.RED, bold=True), err=True)
        if debug:
            raise
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(typer.style(f"Evaluation Error: {e}", fg=typer.colors.RED, bold=True), err=True)
        if debug:
            raise
        raise typer.Exit(code=1)
    finally:
        db.close()


@app.command("redteam")
def redteam(
    target: str = typer.Option("demorrag", "--target", "-t", help="Target AI application identifier ('mock' or 'demorrag')"),
    dataset: str | None = typer.Option(
        None,
        "--dataset",
        "-d",
        help="Specific red-team attack dataset JSON path",
    ),
    category: str | None = typer.Option(
        None,
        "--category",
        "-c",
        help="Specific attack category (prompt_injection, jailbreak, instruction_override, data_leakage, tool_abuse)",
    ),
    debug: bool = typer.Option(False, "--debug", help="Enable verbose debug output and tracebacks"),
) -> None:
    """Run adversarial red-team probe suite against target application."""
    target_key = target.lower()
    if target_key in ["demorrag", "rag"]:
        target_adapter = DemoRAGAdapter()
    else:
        target_adapter = MockTargetAdapter()

    repo_root = Path(__file__).resolve().parents[2]
    redteam_dir = repo_root / "datasets" / "redteam"
    if not redteam_dir.is_dir():
        redteam_dir = Path("datasets/redteam").resolve()

    cases: list[RedTeamCase] = []

    if dataset:
        cases = RedTeamDatasetLoader.load_from_file(dataset)
    else:
        # Load all red-team dataset files
        dataset_files = ["injection.json", "jailbreak.json", "leakage.json", "tool_abuse.json"]
        for fname in dataset_files:
            fpath = redteam_dir / fname
            if fpath.is_file():
                cases.extend(RedTeamDatasetLoader.load_from_file(fpath))

    if category:
        cat_norm = category.lower().strip()
        cases = [c for c in cases if c.category.value == cat_norm or cat_norm in c.category.value]

    typer.echo("PROBENEST RED-TEAM EVALUATION\n")
    typer.echo(f"Target: {target}\n")

    init_db()
    db = SessionLocal()
    try:
        service = RedTeamService(db)
        run_record = service.run_redteam(
            dataset_path_or_cases=cases,
            target_adapter=target_adapter,
            target_name=target,
            category_filter=category,
        )

        # Group results by category
        category_summary: dict[str, dict[str, int]] = {}
        for r in run_record.results:
            cat_name = r.category.value.replace("_", " ").title()
            if cat_name not in category_summary:
                category_summary[cat_name] = {"total": 0, "defended": 0, "failed": 0}
            category_summary[cat_name]["total"] += 1
            if r.passed:
                category_summary[cat_name]["defended"] += 1
            else:
                category_summary[cat_name]["failed"] += 1

        for cat_name, stats in category_summary.items():
            typer.echo(typer.style(cat_name, bold=True))
            defended = stats["defended"]
            total = stats["total"]
            failed = stats["failed"]

            defended_str = typer.style(f"  {defended}/{total} defended", fg=typer.colors.GREEN if failed == 0 else typer.colors.YELLOW)
            failed_str = typer.style(f"  {failed} failures\n", fg=typer.colors.RED if failed > 0 else typer.colors.GREEN)
            typer.echo(defended_str)
            typer.echo(failed_str)

        typer.echo(typer.style(f"TOTAL TESTS: {run_record.total_cases}", bold=True))
        typer.echo(typer.style(f"FAILURES: {run_record.failed_cases}", fg=typer.colors.RED if run_record.failed_cases > 0 else typer.colors.GREEN, bold=True))
        typer.echo(typer.style(f"High-risk failures: {run_record.high_critical_failures}\n", fg=typer.colors.RED if run_record.high_critical_failures > 0 else typer.colors.GREEN, bold=True))

        # Display failure details
        if run_record.failed_cases > 0:
            typer.echo(typer.style("FAILURE DETAILS", bold=True, fg=typer.colors.RED))
            typer.echo("-" * 40)
            for r in run_record.results:
                if not r.passed:
                    typer.echo(f"ID: {r.test_id}")
                    typer.echo(f"Category: {r.category.value}")
                    typer.echo(f"Severity: {r.severity.value.upper()}")
                    typer.echo(f"Attack: {r.attack}")
                    typer.echo(f"Expected: {r.expected_behavior}")
                    typer.echo(f"Actual: {r.actual_output[:120]}...")
                    typer.echo(f"Reason: {r.reason}")
                    typer.echo("-" * 40)

    except Exception as e:
        typer.echo(typer.style(f"Red-Team Execution Error: {e}", fg=typer.colors.RED, bold=True), err=True)
        if debug:
            raise
        raise typer.Exit(code=1)
    finally:
        db.close()


@app.command("score")
def score_cmd(
    run_id: str = typer.Argument(..., help="Run ID to calculate and display scores for"),
    format: str = typer.Option("text", "--format", "-f", help="Output format ('text' or 'json')"),
) -> None:
    """Calculate and display Quality, Security, and Overall Reliability scores for a run."""
    init_db()
    db = SessionLocal()
    try:
        score_repo = ScoreRepository(db)
        eval_repo = EvaluationRepository(db)
        rt_repo = RedTeamRepository(db)

        score = score_repo.get_score(run_id)

        if not score:
            # Try calculating score dynamically if run exists
            eval_run = eval_repo.get_run_by_id(run_id)
            rt_run = rt_repo.get_run(run_id)

            if not eval_run and not rt_run:
                typer.echo(typer.style(f"Error: Run with ID '{run_id}' not found.", fg=typer.colors.RED, bold=True), err=True)
                raise typer.Exit(code=1)

            engine = ScoreEngine()
            score = engine.calculate_run_score(
                run_id=run_id,
                target=eval_run.target if eval_run else (rt_run.target if rt_run else "demorrag"),
                eval_run=eval_run,
                redteam_run=rt_run,
            )
            score_repo.save_score(score)

        if format.lower() == "json":
            typer.echo(json.dumps(score.model_dump(), indent=2, default=str))
            return

        typer.echo("PROBENEST RUN SCORE SUMMARY\n")
        typer.echo(f"Run ID: {score.run_id}")
        typer.echo(f"Target: {score.target}\n")

        typer.echo(typer.style("QUALITY SCORE", bold=True))
        typer.echo(f"  Score: {score.quality_score.score * 100:.1f}% ({score.quality_score.score:.4f})")
        for m, s in score.quality_score.evaluator_scores.items():
            typer.echo(f"    - {m}: {s:.2f}")

        typer.echo("\n" + typer.style("SECURITY SCORE", bold=True))
        typer.echo(f"  Score: {score.security_score.score * 100:.1f}% ({score.security_score.score:.4f})")
        typer.echo(f"  Defended: {score.security_score.defended_cases}/{score.security_score.total_cases}")
        typer.echo(f"  High/Critical Failures: {score.security_score.high_critical_failures}")

        typer.echo("\n" + typer.style("OVERALL RELIABILITY SCORE", bold=True))
        typer.echo(f"  Score: {score.overall_score.score * 100:.1f}% ({score.overall_score.score:.4f})\n")

    finally:
        db.close()


@app.command("compare")
def compare_cmd(
    baseline: str = typer.Argument(..., help="Baseline run ID"),
    candidate: str = typer.Argument(..., help="Candidate run ID"),
    format: str = typer.Option("text", "--format", "-f", help="Output format ('text' or 'json')"),
) -> None:
    """Compare evaluation run iterations and perform regression detection."""
    init_db()
    db = SessionLocal()
    try:
        score_repo = ScoreRepository(db)
        eval_repo = EvaluationRepository(db)
        rt_repo = RedTeamRepository(db)
        engine = ScoreEngine()
        reg_engine = RegressionEngine()

        def _get_or_calc_score(run_id: str):
            s = score_repo.get_score(run_id)
            e_run = eval_repo.get_run_by_id(run_id)
            rt_run = rt_repo.get_run(run_id)
            if not s and (e_run or rt_run):
                target = e_run.target if e_run else (rt_run.target if rt_run else "demorrag")
                s = engine.calculate_run_score(run_id=run_id, target=target, eval_run=e_run, redteam_run=rt_run)
                score_repo.save_score(s)
            return s, e_run, rt_run

        b_score, b_eval_run, b_rt_run = _get_or_calc_score(baseline)
        c_score, c_eval_run, c_rt_run = _get_or_calc_score(candidate)

        if not b_score or not c_score:
            missing = baseline if not b_score else candidate
            typer.echo(typer.style(f"Error: Run ID '{missing}' not found for comparison.", fg=typer.colors.RED, bold=True), err=True)
            raise typer.Exit(code=1)

        reg_result = reg_engine.compare_scores(
            baseline_score=b_score,
            candidate_score=c_score,
            baseline_eval_run=b_eval_run,
            candidate_eval_run=c_eval_run,
            baseline_redteam_run=b_rt_run,
            candidate_redteam_run=c_rt_run,
        )

        if format.lower() == "json":
            typer.echo(json.dumps(reg_result.model_dump(), indent=2, default=str))
            return

        comp = reg_result.comparison

        typer.echo("PROBENEST RUN COMPARISON\n")
        typer.echo(f"Baseline:  {comp.baseline_run_id}")
        typer.echo(f"Candidate: {comp.candidate_run_id}")
        typer.echo(f"Target:    {comp.target}\n")

        if comp.warning:
            typer.echo(typer.style(f"WARNING: {comp.warning}\n", fg=typer.colors.YELLOW, bold=True))

        # Quality
        typer.echo(typer.style("QUALITY", bold=True))
        typer.echo(f"  Baseline:  {b_score.quality_score.score:.4f}")
        typer.echo(f"  Candidate: {c_score.quality_score.score:.4f}")
        q_symbol = "ALERT" if comp.quality_delta <= -0.05 else ("UP" if comp.quality_delta > 0 else "=")
        typer.echo(f"  Delta:    {comp.quality_delta:+.4f}  {q_symbol}\n")

        # Security
        typer.echo(typer.style("SECURITY", bold=True))
        typer.echo(f"  Baseline:  {b_score.security_score.score:.4f}")
        typer.echo(f"  Candidate: {c_score.security_score.score:.4f}")
        sec_symbol = "ALERT" if comp.security_delta <= -0.05 else ("UP" if comp.security_delta > 0 else "=")
        typer.echo(f"  Delta:    {comp.security_delta:+.4f}  {sec_symbol}\n")

        # Overall
        typer.echo(typer.style("OVERALL", bold=True))
        typer.echo(f"  Baseline:  {b_score.overall_score.score:.4f}")
        typer.echo(f"  Candidate: {c_score.overall_score.score:.4f}")
        ov_symbol = "ALERT" if comp.overall_delta <= -0.05 else ("UP" if comp.overall_delta > 0 else "=")
        typer.echo(f"  Delta:    {comp.overall_delta:+.4f}  {ov_symbol}\n")

        # Regression details
        if reg_result.detected:
            typer.echo(typer.style(f"REGRESSION DETECTED (Severity: {reg_result.severity})", fg=typer.colors.RED, bold=True))
            for r in reg_result.reasons:
                typer.echo(f"  - {r}")
            typer.echo("")
        else:
            typer.echo(typer.style("NO REGRESSION DETECTED\n", fg=typer.colors.GREEN, bold=True))

        if comp.new_failures:
            typer.echo(typer.style("New failures:", bold=True, fg=typer.colors.RED))
            for nf in comp.new_failures:
                typer.echo(f"  {nf.test_id:<12} {nf.severity:<8} ({nf.category_or_evaluator})")

        if comp.fixed_failures:
            typer.echo(typer.style("\nFixed failures:", bold=True, fg=typer.colors.GREEN))
            for ff in comp.fixed_failures:
                typer.echo(f"  {ff.test_id:<12} {ff.severity:<8} ({ff.category_or_evaluator})")

        if comp.persistent_failures:
            typer.echo(typer.style("\nPersistent failures:", bold=True, fg=typer.colors.YELLOW))
            for pf in comp.persistent_failures:
                typer.echo(f"  {pf.test_id:<12} {pf.severity:<8} ({pf.category_or_evaluator})")

        typer.echo("")

    finally:
        db.close()


if __name__ == "__main__":
    app()
