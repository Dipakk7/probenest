from app.db.database import SessionLocal, init_db
from app.domain.evaluator import EvaluationResult
from app.domain.run import EvaluationRun, RunStatus
from app.repositories.evaluation_repository import EvaluationRepository


def test_repository_save_and_retrieve_run() -> None:
    """Test persisting an EvaluationRun and fetching it back from SQLite."""
    init_db()
    db = SessionLocal()
    try:
        repo = EvaluationRepository(db)
        result = EvaluationResult(
            test_id="test_01",
            evaluator="ExactMatchEvaluator",
            passed=True,
            score=1.0,
            reason="Match",
        )
        run = EvaluationRun(
            run_id="repo_run_001",
            status=RunStatus.COMPLETED,
            total_cases=1,
            passed_cases=1,
            failed_cases=0,
            results=[result],
        )

        saved = repo.save_run(run)
        assert saved.run_id == "repo_run_001"

        fetched = repo.get_run_by_id("repo_run_001")
        assert fetched is not None
        assert fetched.run_id == "repo_run_001"
        assert len(fetched.results) == 1
        assert fetched.results[0].test_id == "test_01"

        runs_list = repo.list_runs()
        assert len(runs_list) >= 1
    finally:
        db.close()
