from pathlib import Path

import typer

from app.adapters.demo_rag import DemoRAGAdapter
from app.adapters.mock_target import MockTargetAdapter
from app.db.database import SessionLocal, init_db
from app.domain.redteam import RedTeamCase
from app.evaluators.registry import get_evaluators_by_names
from app.loaders.dataset import DatasetLoadError
from app.loaders.redteam_loader import RedTeamDatasetLoader
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


@app.command("compare")
def compare(
    run_a: str = typer.Argument(..., help="First run ID or model version"),
    run_b: str = typer.Argument(..., help="Second run ID or model version"),
) -> None:
    """Compare evaluation results across model or prompt iterations."""
    typer.echo(f"Comparing evaluation runs: '{run_a}' vs '{run_b}'...")
    typer.echo("Probenest compare engine is not implemented yet.")
    typer.echo("Available in a future phase.")


if __name__ == "__main__":
    app()
