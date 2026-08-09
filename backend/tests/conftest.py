from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.database import Base
from app.domain.evaluator import EvaluationResult
from app.domain.redteam import AttackCategory, RedTeamResult, RedTeamRun, Severity
from app.domain.run import EvaluationRun


@pytest.fixture
def isolated_db(tmp_path) -> Generator[Session, None, None]:
    """Create an isolated, temporary SQLite database session in tmp_path for each test."""
    db_file = tmp_path / "test_probenest.db"
    database_url = f"sqlite:///{db_file}"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def synthetic_eval_run() -> EvaluationRun:
    """Create a synthetic EvaluationRun with deterministic quality results."""
    return EvaluationRun(
        run_id="run_synth_eval_01",
        target="demorrag",
        total_cases=2,
        passed_cases=2,
        results=[
            EvaluationResult(test_id="qa_001", evaluator="AccuracyEvaluator", passed=True, score=1.0, reason="pass"),
            EvaluationResult(test_id="qa_002", evaluator="RelevanceEvaluator", passed=True, score=1.0, reason="pass"),
        ],
    )


@pytest.fixture
def synthetic_redteam_run() -> RedTeamRun:
    """Create a synthetic RedTeamRun with deterministic red-team defense results."""
    return RedTeamRun(
        run_id="rt_synth_01",
        target="demorrag",
        total_cases=2,
        passed_cases=2,
        failed_cases=0,
        high_critical_failures=0,
        results=[
            RedTeamResult(
                test_id="SEC-INJ-001",
                category=AttackCategory.PROMPT_INJECTION,
                attack="attack 1",
                passed=True,
                severity=Severity.HIGH,
                reason="defended",
                actual_output="refused",
                expected_behavior="refuse",
            ),
            RedTeamResult(
                test_id="SEC-JBK-001",
                category=AttackCategory.JAILBREAK,
                attack="attack 2",
                passed=True,
                severity=Severity.CRITICAL,
                reason="defended",
                actual_output="refused",
                expected_behavior="refuse",
            ),
        ],
    )
