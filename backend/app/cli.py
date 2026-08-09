from pathlib import Path

import typer

from app.db.database import SessionLocal, init_db
from app.loaders.dataset import DatasetLoadError
from app.services.evaluation_service import EvaluationService

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
    target: str = typer.Option("default", "--target", "-t", help="Target AI application identifier"),
    dataset: str = typer.Option(
        "../datasets/golden/example.json",
        "--dataset",
        "-d",
        help="Evaluation dataset JSON file path",
    ),
    debug: bool = typer.Option(False, "--debug", help="Enable verbose debug output and tracebacks"),
) -> None:
    """Run AI evaluation pipeline against target application using specified dataset."""
    dataset_path = Path(dataset)
    if not dataset_path.is_file():
        # Fallback check relative to repo root
        root_dataset_path = Path(__file__).resolve().parent.parent.parent / "datasets" / "golden" / "example.json"
        if root_dataset_path.is_file():
            dataset_path = root_dataset_path

    typer.echo("PROBENEST EVALUATION\n")
    typer.echo(f"Target: {target}")
    typer.echo(f"Dataset: {dataset_path}\n")

    init_db()
    db = SessionLocal()
    try:
        service = EvaluationService(db)
        run_record = service.run_evaluation(dataset_path_or_cases=dataset_path)

        typer.echo(f"Run: {run_record.run_id}")
        typer.echo(f"Status: {run_record.status.value.upper()}")
        typer.echo(f"Cases: {run_record.total_cases}")
        typer.echo(f"Passed: {run_record.passed_cases}")
        typer.echo(f"Failed: {run_record.failed_cases}\n")

        typer.echo("Results:")
        for res in run_record.results:
            status_label = "PASS" if res.passed else "FAIL"
            color = typer.colors.GREEN if res.passed else typer.colors.RED
            formatted_status = typer.style(f"  {status_label}", fg=color, bold=True)
            typer.echo(f"{formatted_status} {res.test_id} ({res.evaluator}): {res.reason}")

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
