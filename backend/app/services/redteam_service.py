from pathlib import Path

from sqlalchemy.orm import Session

from app.domain.redteam import RedTeamCase, RedTeamRun
from app.domain.target import TargetAdapter
from app.loaders.redteam_loader import RedTeamDatasetLoader
from app.redteam.runner import RedTeamRunner
from app.repositories.redteam_repository import RedTeamRepository


class RedTeamService:
    """Service layer coordinating red-team evaluation runs, persistence, and querying."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = RedTeamRepository(db)

    def run_redteam(
        self,
        dataset_path_or_cases: str | Path | list[RedTeamCase],
        target_adapter: TargetAdapter,
        target_name: str = "demorrag",
        category_filter: str | None = None,
    ) -> RedTeamRun:
        """Execute a red-team evaluation run and persist results."""
        if isinstance(dataset_path_or_cases, (str, Path)):
            cases = RedTeamDatasetLoader.load_from_file(dataset_path_or_cases)
        else:
            cases = list(dataset_path_or_cases)

        if category_filter:
            cat_norm = category_filter.lower().strip()
            cases = [c for c in cases if c.category.value == cat_norm or cat_norm in c.category.value]

        runner = RedTeamRunner(target_adapter=target_adapter)
        run_record = runner.run(cases=cases, target_name=target_name)

        return self.repo.save_run(run_record)

    def get_run(self, run_id: str) -> RedTeamRun | None:
        """Retrieve a red-team run by ID."""
        return self.repo.get_run(run_id)

    def list_runs(self, limit: int = 50, offset: int = 0) -> list[RedTeamRun]:
        """List historical red-team runs."""
        return self.repo.list_runs(limit=limit, offset=offset)
