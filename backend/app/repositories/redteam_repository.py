import json
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import RedTeamResultModel, RedTeamRunModel
from app.domain.redteam import AttackCategory, RedTeamResult, RedTeamRun, Severity


class RedTeamRepository:
    """Repository for persisting and retrieving adversarial red-team run records."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def save_run(self, run: RedTeamRun) -> RedTeamRun:
        """Save a RedTeamRun and its associated RedTeamResult records."""
        run_model = RedTeamRunModel(
            id=run.run_id,
            target=run.target,
            status=run.status,
            started_at=run.started_at,
            completed_at=run.completed_at,
            total_cases=run.total_cases,
            passed_cases=run.passed_cases,
            failed_cases=run.failed_cases,
            high_critical_failures=run.high_critical_failures,
        )
        self.db.add(run_model)

        for r in run.results:
            result_model = RedTeamResultModel(
                run_id=run.run_id,
                test_id=r.test_id,
                category=r.category.value if isinstance(r.category, AttackCategory) else str(r.category),
                attack=r.attack,
                passed=r.passed,
                severity=r.severity.value if isinstance(r.severity, Severity) else str(r.severity),
                reason=r.reason,
                actual_output=r.actual_output,
                expected_behavior=r.expected_behavior,
                evidence_json=json.dumps(r.evidence) if r.evidence else None,
            )
            self.db.add(result_model)

        self.db.commit()
        return run

    def get_run(self, run_id: str) -> RedTeamRun | None:
        """Retrieve a RedTeamRun by run ID."""
        stmt = select(RedTeamRunModel).where(RedTeamRunModel.id == run_id)
        run_model = self.db.scalar(stmt)
        if not run_model:
            return None

        results = [
            RedTeamResult(
                test_id=rm.test_id,
                category=AttackCategory(rm.category),
                attack=rm.attack,
                passed=rm.passed,
                severity=Severity(rm.severity),
                reason=rm.reason,
                actual_output=rm.actual_output,
                expected_behavior=rm.expected_behavior,
                evidence=json.loads(rm.evidence_json) if rm.evidence_json else {},
            )
            for rm in run_model.results
        ]

        return RedTeamRun(
            run_id=run_model.id,
            target=run_model.target,
            started_at=run_model.started_at,
            completed_at=run_model.completed_at,
            status=run_model.status,
            total_cases=run_model.total_cases,
            passed_cases=run_model.passed_cases,
            failed_cases=run_model.failed_cases,
            high_critical_failures=run_model.high_critical_failures,
            results=results,
        )

    def list_runs(self, limit: int = 50, offset: int = 0) -> list[RedTeamRun]:
        """List historical red-team runs ordered by start time descending."""
        stmt = (
            select(RedTeamRunModel)
            .order_by(RedTeamRunModel.started_at.desc())
            .limit(limit)
            .offset(offset)
        )
        models: Sequence[RedTeamRunModel] = self.db.scalars(stmt).all()
        return [
            RedTeamRun(
                run_id=m.id,
                target=m.target,
                started_at=m.started_at,
                completed_at=m.completed_at,
                status=m.status,
                total_cases=m.total_cases,
                passed_cases=m.passed_cases,
                failed_cases=m.failed_cases,
                high_critical_failures=m.high_critical_failures,
            )
            for m in models
        ]
