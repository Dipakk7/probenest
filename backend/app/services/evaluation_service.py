from collections.abc import Sequence
from pathlib import Path

from sqlalchemy.orm import Session

from app.adapters.mock_target import MockTargetAdapter
from app.domain.case import EvaluationCase
from app.domain.evaluator import Evaluator
from app.domain.run import EvaluationRun
from app.domain.target import TargetAdapter
from app.evaluators.exact_match import ExactMatchEvaluator
from app.loaders.dataset import DatasetLoader
from app.repositories.evaluation_repository import EvaluationRepository
from app.repositories.score_repository import ScoreRepository
from app.runner.runner import EvaluationRunner
from app.scoring.engine import ScoreEngine


class EvaluationService:
    """High-level application service managing evaluation workflows, scores, and database persistence."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = EvaluationRepository(db)
        self.score_repo = ScoreRepository(db)
        self.score_engine = ScoreEngine()

    def run_evaluation(
        self,
        dataset_path_or_cases: str | Path | Sequence[EvaluationCase],
        target_adapter: TargetAdapter | None = None,
        evaluators: Sequence[Evaluator] | None = None,
        target_name: str = "demorrag",
        run_id: str | None = None,
    ) -> EvaluationRun:
        """Load dataset, execute evaluation runner, calculate run score, persist run details, and return completed EvaluationRun."""
        if isinstance(dataset_path_or_cases, (str, Path)):
            cases = DatasetLoader.load_from_file(dataset_path_or_cases)
        else:
            cases = list(dataset_path_or_cases)

        adapter = target_adapter or MockTargetAdapter()
        evals = evaluators or [ExactMatchEvaluator()]

        runner = EvaluationRunner(target_adapter=adapter, evaluators=evals)
        run_result = runner.run(cases=cases, run_id=run_id)

        saved_run = self.repository.save_run(run_result)

        # Calculate and persist run score
        run_score = self.score_engine.calculate_run_score(
            run_id=saved_run.run_id,
            target=target_name,
            quality_results=saved_run.results,
        )
        self.score_repo.save_score(run_score)

        return saved_run

    def get_run(self, run_id: str) -> EvaluationRun | None:
        """Retrieve evaluation run by ID."""
        return self.repository.get_run_by_id(run_id)

    def list_runs(self, limit: int = 50, offset: int = 0) -> list[EvaluationRun]:
        """List historical evaluation runs."""
        return self.repository.list_runs(limit=limit, offset=offset)
