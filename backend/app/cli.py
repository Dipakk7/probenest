import typer

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
    dataset: str = typer.Option("golden", "--dataset", "-d", help="Evaluation dataset path or name"),
) -> None:
    """Run AI evaluation pipeline against target application."""
    typer.echo(f"Evaluating target '{target}' using dataset '{dataset}'...")
    typer.echo("Probenest evaluation engine is not implemented yet.")
    typer.echo("Available in a future phase.")


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
