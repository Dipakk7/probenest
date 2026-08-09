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
from app.reports.json_report import JSONReportGenerator
from app.reports.markdown_report import MarkdownReportGenerator
from app.reports.service import ReportService
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
    format: str = typer.Option("text", "--format", "-f", help="Output format ('text', 'json', or 'markdown')"),
    output: str | None = typer.Option(None, "--output", "-o", help="File path to write report output"),
    debug: bool = typer.Option(False, "--debug", help="Enable verbose debug output and tracebacks"),
) -> None:
    """Run AI quality evaluation pipeline against target application. (Exit Code 0 on completion)."""
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

        report_svc = ReportService(db)
        run_report = report_svc.generate_run_report(run_record.run_id)

        if output:
            if output.endswith(".json") or format.lower() == "json":
                JSONReportGenerator.write_json_file(run_report, output)
            else:
                MarkdownReportGenerator.write_markdown_file(run_report, output)
            typer.echo(f"Evaluation report written to {output}")
            return

        if format.lower() == "json":
            typer.echo(JSONReportGenerator.generate_json_string(run_report))
            return
        elif format.lower() == "markdown":
            typer.echo(MarkdownReportGenerator.generate_markdown(run_report))
            return

        typer.echo("PROBENEST QUALITY EVALUATION\n")
        typer.echo(f"Target: {target}")
        typer.echo(f"Dataset: {dataset_path}\n")
        typer.echo(f"Run: {run_record.run_id}")
        typer.echo(f"Status: {run_record.status.value.upper()}")
        typer.echo(f"Cases: {run_record.total_cases}\n")

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
        raise typer.Exit(code=2)
    except Exception as e:
        typer.echo(typer.style(f"Evaluation Error: {e}", fg=typer.colors.RED, bold=True), err=True)
        if debug:
            raise
        raise typer.Exit(code=3)
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
    format: str = typer.Option("text", "--format", "-f", help="Output format ('text', 'json', or 'markdown')"),
    output: str | None = typer.Option(None, "--output", "-o", help="File path to write report output"),
    debug: bool = typer.Option(False, "--debug", help="Enable verbose debug output and tracebacks"),
) -> None:
    """Run adversarial red-team probe suite against target application. (Exit Code 0 on completion)."""
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
        dataset_files = ["injection.json", "jailbreak.json", "leakage.json", "tool_abuse.json"]
        for fname in dataset_files:
            fpath = redteam_dir / fname
            if fpath.is_file():
                cases.extend(RedTeamDatasetLoader.load_from_file(fpath))

    if category:
        cat_norm = category.lower().strip()
        cases = [c for c in cases if c.category.value == cat_norm or cat_norm in c.category.value]

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

        report_svc = ReportService(db)
        run_report = report_svc.generate_run_report(run_record.run_id)

        if output:
            if output.endswith(".json") or format.lower() == "json":
                JSONReportGenerator.write_json_file(run_report, output)
            else:
                MarkdownReportGenerator.write_markdown_file(run_report, output)
            typer.echo(f"Red-team report written to {output}")
            return

        if format.lower() == "json":
            typer.echo(JSONReportGenerator.generate_json_string(run_report))
            return
        elif format.lower() == "markdown":
            typer.echo(MarkdownReportGenerator.generate_markdown(run_report))
            return

        typer.echo("PROBENEST RED-TEAM EVALUATION\n")
        typer.echo(f"Target: {target}\n")

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

    except DatasetLoadError as e:
        typer.echo(typer.style(f"Red-Team Dataset Error: {e}", fg=typer.colors.RED, bold=True), err=True)
        if debug:
            raise
        raise typer.Exit(code=2)
    except Exception as e:
        typer.echo(typer.style(f"Red-Team Execution Error: {e}", fg=typer.colors.RED, bold=True), err=True)
        if debug:
            raise
        raise typer.Exit(code=3)
    finally:
        db.close()


@app.command("score")
def score_cmd(
    run_id: str = typer.Argument(..., help="Run ID to calculate and display scores for"),
    format: str = typer.Option("text", "--format", "-f", help="Output format ('text', 'json', or 'markdown')"),
    output: str | None = typer.Option(None, "--output", "-o", help="File path to write report output"),
) -> None:
    """Calculate and display Quality, Security, and Overall Reliability scores for a run. (Exit Code 0)."""
    init_db()
    db = SessionLocal()
    try:
        report_svc = ReportService(db)
        try:
            run_report = report_svc.generate_run_report(run_id)
        except ValueError:
            typer.echo(typer.style(f"Error: Run with ID '{run_id}' not found.", fg=typer.colors.RED, bold=True), err=True)
            raise typer.Exit(code=2)

        if output:
            if output.endswith(".json") or format.lower() == "json":
                JSONReportGenerator.write_json_file(run_report, output)
            else:
                MarkdownReportGenerator.write_markdown_file(run_report, output)
            typer.echo(f"Score report written to {output}")
            return

        if format.lower() == "json":
            typer.echo(JSONReportGenerator.generate_json_string(run_report))
            return
        elif format.lower() == "markdown":
            typer.echo(MarkdownReportGenerator.generate_markdown(run_report))
            return

        typer.echo("PROBENEST RUN SCORE SUMMARY\n")
        typer.echo(f"Run ID: {run_report.run.run_id}")
        typer.echo(f"Target: {run_report.run.target}\n")

        # Quality Score
        typer.echo(typer.style("QUALITY SCORE", bold=True))
        if run_report.quality.available and run_report.quality.quality_score is not None:
            typer.echo(f"  Score: {run_report.quality.quality_score * 100:.1f}% ({run_report.quality.quality_score:.4f})")
            for m, s in run_report.quality.evaluator_scores.items():
                typer.echo(f"    - {m}: {s:.2f}")
        else:
            typer.echo("  Score: N/A (No quality tests executed)")

        # Security Score
        typer.echo("\n" + typer.style("SECURITY SCORE", bold=True))
        if run_report.security.available and run_report.security.security_score is not None:
            typer.echo(f"  Score: {run_report.security.security_score * 100:.1f}% ({run_report.security.security_score:.4f})")
            typer.echo(f"  Defended: {run_report.security.defended_cases}/{run_report.security.total_cases}")
            typer.echo(f"  High/Critical Failures: {run_report.security.high_critical_failures}")
        else:
            typer.echo("  Score: N/A (No red-team tests executed)")

        # Overall Score
        typer.echo("\n" + typer.style("OVERALL RELIABILITY SCORE", bold=True))
        if run_report.overall.reliability_score is not None:
            typer.echo(f"  Score: {run_report.overall.reliability_score * 100:.1f}% ({run_report.overall.reliability_score:.4f})\n")
        else:
            typer.echo("  Score: N/A\n")

    except typer.Exit:
        raise
    except Exception as e:  # noqa: BLE001
        typer.echo(typer.style(f"Score Error: {e}", fg=typer.colors.RED, bold=True), err=True)
        raise typer.Exit(code=3)
    finally:
        db.close()


@app.command("compare")
def compare_cmd(
    baseline: str = typer.Argument(..., help="Baseline run ID"),
    candidate: str = typer.Argument(..., help="Candidate run ID"),
    format: str = typer.Option("text", "--format", "-f", help="Output format ('text', 'json', or 'markdown')"),
    output: str | None = typer.Option(None, "--output", "-o", help="File path to write comparison output"),
) -> None:
    """Compare evaluation run iterations and perform regression detection. (Exit 0 = no regression, Exit 1 = regression detected)."""
    init_db()
    db = SessionLocal()
    try:
        report_svc = ReportService(db)
        try:
            cand_report = report_svc.generate_run_report(candidate, baseline_run_id=baseline)
        except ValueError as e:
            typer.echo(typer.style(f"Error: {e}", fg=typer.colors.RED, bold=True), err=True)
            raise typer.Exit(code=2)

        reg_result = cand_report.regression
        if not reg_result:
            typer.echo(typer.style(f"Error: Could not generate comparison for '{baseline}' and '{candidate}'.", fg=typer.colors.RED, bold=True), err=True)
            raise typer.Exit(code=2)

        if output:
            if output.endswith(".json") or format.lower() == "json":
                JSONReportGenerator.write_json_file(cand_report, output)
            else:
                MarkdownReportGenerator.write_markdown_file(cand_report, output)
            typer.echo(f"Comparison report written to {output}")
            raise typer.Exit(code=1 if reg_result.detected else 0)

        if format.lower() == "json":
            typer.echo(json.dumps(reg_result.model_dump(), indent=2, default=str))
            raise typer.Exit(code=1 if reg_result.detected else 0)
        elif format.lower() == "markdown":
            typer.echo(MarkdownReportGenerator.generate_markdown(cand_report))
            raise typer.Exit(code=1 if reg_result.detected else 0)

        comp = reg_result.comparison
        score_repo = ScoreRepository(db)
        eval_repo = EvaluationRepository(db)
        rt_repo = RedTeamRepository(db)
        engine = ScoreEngine()

        def _get_score(rid: str):
            s = score_repo.get_score(rid)
            if not s:
                e_run = eval_repo.get_run_by_id(rid)
                rt_run = rt_repo.get_run(rid)
                if e_run or rt_run:
                    t = e_run.target if e_run else (rt_run.target if rt_run else "demorrag")
                    s = engine.calculate_run_score(rid, t, eval_run=e_run, redteam_run=rt_run)
            return s

        b_score = _get_score(baseline)
        c_score = _get_score(candidate)

        typer.echo("PROBENEST RUN COMPARISON\n")
        typer.echo(f"Baseline:  {comp.baseline_run_id}")
        typer.echo(f"Candidate: {comp.candidate_run_id}")
        typer.echo(f"Target:    {comp.target}\n")

        if comp.warning:
            typer.echo(typer.style(f"WARNING: {comp.warning}\n", fg=typer.colors.YELLOW, bold=True))

        # Quality
        typer.echo(typer.style("QUALITY", bold=True))
        typer.echo(f"  Baseline:  {b_score.quality_score.score * 100:.1f}%")
        typer.echo(f"  Candidate: {c_score.quality_score.score * 100:.1f}%")
        q_symbol = "ALERT" if comp.quality_delta <= -0.05 else ("UP" if comp.quality_delta > 0 else "=")
        typer.echo(f"  Delta:    {comp.quality_delta * 100:+.2f} pp  {q_symbol}\n")

        # Security
        typer.echo(typer.style("SECURITY", bold=True))
        typer.echo(f"  Baseline:  {b_score.security_score.score * 100:.1f}%")
        typer.echo(f"  Candidate: {c_score.security_score.score * 100:.1f}%")
        sec_symbol = "ALERT" if comp.security_delta <= -0.05 else ("UP" if comp.security_delta > 0 else "=")
        typer.echo(f"  Delta:    {comp.security_delta * 100:+.2f} pp  {sec_symbol}\n")

        # Overall
        typer.echo(typer.style("OVERALL", bold=True))
        typer.echo(f"  Baseline:  {b_score.overall_score.score * 100:.1f}%")
        typer.echo(f"  Candidate: {c_score.overall_score.score * 100:.1f}%")
        ov_symbol = "ALERT" if comp.overall_delta <= -0.05 else ("UP" if comp.overall_delta > 0 else "=")
        typer.echo(f"  Delta:    {comp.overall_delta * 100:+.2f} pp  {ov_symbol}\n")

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
        raise typer.Exit(code=1 if reg_result.detected else 0)

    except typer.Exit:
        raise
    except Exception as e:  # noqa: BLE001
        typer.echo(typer.style(f"Compare Error: {e}", fg=typer.colors.RED, bold=True), err=True)
        raise typer.Exit(code=3)
    finally:
        db.close()


@app.command("report")
def report_cmd(
    run_id: str = typer.Argument(..., help="Run ID to generate comprehensive report for"),
    baseline: str | None = typer.Option(None, "--baseline", "-b", help="Optional baseline run ID to include regression comparison"),
    format: str = typer.Option("all", "--format", "-f", help="Report format ('all', 'json', or 'markdown')"),
    output: str | None = typer.Option(None, "--output", "-o", help="Custom output directory or file path"),
) -> None:
    """Generate comprehensive JSON and Markdown evaluation reports. (Exit Code 0)."""
    init_db()
    db = SessionLocal()
    try:
        report_svc = ReportService(db)
        try:
            run_report = report_svc.generate_run_report(run_id, baseline_run_id=baseline)
        except ValueError as e:
            typer.echo(typer.style(f"Error: {e}", fg=typer.colors.RED, bold=True), err=True)
            raise typer.Exit(code=2)

        if output:
            out_path = Path(output)
            if out_path.suffix.lower() == ".json" or format.lower() == "json":
                JSONReportGenerator.write_json_file(run_report, str(out_path))
                typer.echo(f"Report JSON written to {out_path}")
                return
            elif out_path.suffix.lower() == ".md" or format.lower() in ["markdown", "md"]:
                MarkdownReportGenerator.write_markdown_file(run_report, str(out_path))
                typer.echo(f"Report Markdown written to {out_path}")
                return
            else:
                json_p, md_p = report_svc.write_report_files(run_report, output_dir=out_path)
                typer.echo(f"Report files written to directory {out_path}:")
                typer.echo(f"  - {json_p}")
                typer.echo(f"  - {md_p}")
                return

        if format.lower() == "json":
            typer.echo(JSONReportGenerator.generate_json_string(run_report))
            return

        if format.lower() in ["markdown", "md"]:
            typer.echo(MarkdownReportGenerator.generate_markdown(run_report))
            return

        json_p, md_p = report_svc.write_report_files(run_report)

        typer.echo("PROBENEST REPORT GENERATION\n")
        typer.echo(f"Run ID: {run_id}")
        typer.echo(f"Target: {run_report.run.target}\n")
        typer.echo("Generated Report Files:")
        typer.echo(f"  - JSON:     {json_p}")
        typer.echo(f"  - Markdown: {md_p}\n")

        if run_report.quality.available and run_report.quality.quality_score is not None:
            typer.echo(f"Quality Score:  {run_report.quality.quality_score * 100:.1f}%")
        else:
            typer.echo("Quality Score:  N/A")

        if run_report.security.available and run_report.security.security_score is not None:
            typer.echo(f"Security Score: {run_report.security.security_score * 100:.1f}%")
        else:
            typer.echo("Security Score: N/A")

        if run_report.overall.reliability_score is not None:
            typer.echo(f"Overall Score:  {run_report.overall.reliability_score * 100:.1f}%")
        else:
            typer.echo("Overall Score:  N/A")

        if run_report.regression:
            reg_status = f"REGRESSION DETECTED ({run_report.regression.severity})" if run_report.regression.detected else "NO REGRESSION DETECTED"
            typer.echo(f"Regression:     {reg_status}")
        else:
            typer.echo("Regression:     NOT EVALUATED\n")

    except typer.Exit:
        raise
    except Exception as e:  # noqa: BLE001
        typer.echo(typer.style(f"Report Error: {e}", fg=typer.colors.RED, bold=True), err=True)
        raise typer.Exit(code=3)
    finally:
        db.close()


if __name__ == "__main__":
    app()
