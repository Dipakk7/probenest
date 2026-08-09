import json

from app.db.database import SessionLocal, init_db
from app.reports.json_report import JSONReportGenerator
from app.reports.markdown_report import MarkdownReportGenerator
from app.reports.models import (
    QualityReportSection,
    RunMetadataReport,
    RunReport,
    SecurityReportSection,
)
from app.reports.service import ReportService
from app.services.evaluation_service import EvaluationService


def test_json_and_markdown_generators() -> None:
    """Test JSONReportGenerator and MarkdownReportGenerator schema version and formatting."""
    report = RunReport(
        schema_version="1.0",
        run=RunMetadataReport(run_id="run_test_01", target="mock"),
        quality=QualityReportSection(available=True, quality_score=0.85, evaluator_scores={"Accuracy": 0.85}),
        security=SecurityReportSection(available=False, security_score=None),
    )

    json_str = JSONReportGenerator.generate_json_string(report)
    assert '"schema_version": "1.0"' in json_str
    parsed = json.loads(json_str)
    assert parsed["run"]["run_id"] == "run_test_01"
    assert parsed["quality"]["quality_score"] == 0.85

    md_str = MarkdownReportGenerator.generate_markdown(report)
    assert "# Probenest Evaluation & Reliability Report" in md_str
    assert "Quality Score: 85.00%" in md_str
    assert "Security Score: N/A" in md_str


def test_report_service_file_writing(tmp_path) -> None:
    """Test ReportService generates report objects and writes json/md files."""
    init_db()
    db = SessionLocal()
    try:
        eval_svc = EvaluationService(db)
        eval_run = eval_svc.run_evaluation(dataset_path_or_cases=[], target_name="mock", run_id="run_file_test")

        report_svc = ReportService(db)
        report = report_svc.generate_run_report(eval_run.run_id)
        assert report.run.run_id == "run_file_test"

        output_dir = tmp_path / "reports_out"
        _json_p, _md_p = report_svc.write_report_files(report, output_dir=output_dir)

        assert (tmp_path / "reports_out" / "report.json").is_file()
        assert (tmp_path / "reports_out" / "report.md").is_file()
    finally:
        db.close()
