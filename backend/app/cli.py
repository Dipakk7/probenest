from pathlib import Path

import typer

from app.adapters.demo_rag import DemoRAGAdapter
from app.adapters.mock_target import MockTargetAdapter
from app.db.database import SessionLocal, init_db
from app.evaluators.registry import get_evaluators_by_names
from app.loaders.dataset import DatasetLoadError
from app.services.evaluation_service import EvaluationService
from app.services.quality_service import QualityEvaluationService

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
    target: str = typer.Option("default", "--target", "-t", help="Target AI application identifier"),
    suite: str = typer.Option("all", "--suite", "-s", help="Red-team probe suite (injection, jailbreak, leakage)"),
) -> None:
    """Run adversarial red-teaming probe suite against target application."""
    typer.echo(f"Executing red-team probe suite '{suite}' against target '{target}'...")
    typer.echo("Probenest red-team engine is not implemented yet.")
    typer.echo("Available in a future phase.")


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
