import json

from sqlalchemy.orm import Session

from app.db.models import EvaluationResultModel, EvaluationRunModel
from app.domain.evaluator import EvaluationResult
from app.domain.run import EvaluationRun, RunStatus


class EvaluationRepository:
    """Data access repository for evaluation runs and results in SQLite."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def save_run(self, run: EvaluationRun) -> EvaluationRun:
        """Persist or update an EvaluationRun and its associated EvaluationResult objects."""
        run_model = self.db.query(EvaluationRunModel).filter(EvaluationRunModel.id == run.run_id).first()

        if not run_model:
            run_model = EvaluationRunModel(
                id=run.run_id,
                started_at=run.started_at,
                status=run.status.value if isinstance(run.status, RunStatus) else str(run.status),
                total_cases=run.total_cases,
                passed_cases=run.passed_cases,
                failed_cases=run.failed_cases,
                completed_at=run.completed_at,
            )
            self.db.add(run_model)
        else:
            run_model.status = run.status.value if isinstance(run.status, RunStatus) else str(run.status)
            run_model.total_cases = run.total_cases
            run_model.passed_cases = run.passed_cases
            run_model.failed_cases = run.failed_cases
            run_model.completed_at = run.completed_at

        # Clear old results if re-saving
        self.db.query(EvaluationResultModel).filter(EvaluationResultModel.run_id == run.run_id).delete()

        for res in run.results:
            result_model = EvaluationResultModel(
                run_id=run.run_id,
                test_id=res.test_id,
                evaluator=res.evaluator,
                passed=res.passed,
                score=res.score,
                reason=res.reason,
                severity=res.severity,
                evidence_json=json.dumps(res.evidence or {}),
            )
            self.db.add(result_model)

        self.db.commit()
        self.db.refresh(run_model)
        return self._to_domain_run(run_model)

    def get_run_by_id(self, run_id: str) -> EvaluationRun | None:
        """Fetch an EvaluationRun by its run_id."""
        run_model = self.db.query(EvaluationRunModel).filter(EvaluationRunModel.id == run_id).first()
        if not run_model:
            return None
        return self._to_domain_run(run_model)

    def list_runs(self, limit: int = 50, offset: int = 0) -> list[EvaluationRun]:
        """List historical evaluation runs ordered by started_at descending."""
        models = (
            self.db.query(EvaluationRunModel)
            .order_by(EvaluationRunModel.started_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_domain_run(m) for m in models]

    def _to_domain_run(self, model: EvaluationRunModel) -> EvaluationRun:
        """Convert SQLAlchemy model to domain EvaluationRun Pydantic model."""
        domain_results: list[EvaluationResult] = []
        for r in model.results:
            try:
                evidence_dict = json.loads(r.evidence_json) if r.evidence_json else {}
            except (json.JSONDecodeError, TypeError, ValueError):
                evidence_dict = {}

            domain_results.append(
                EvaluationResult(
                    test_id=r.test_id,
                    evaluator=r.evaluator,
                    passed=r.passed,
                    score=r.score,
                    reason=r.reason,
                    severity=r.severity,
                    evidence=evidence_dict,
                )
            )

        status_enum = RunStatus(model.status) if model.status in RunStatus._value2member_map_ else RunStatus.PENDING

        return EvaluationRun(
            run_id=model.id,
            started_at=model.started_at,
            completed_at=model.completed_at,
            status=status_enum,
            total_cases=model.total_cases,
            passed_cases=model.passed_cases,
            failed_cases=model.failed_cases,
            results=domain_results,
        )
