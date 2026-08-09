from app.domain.evaluator import EvaluationResult
from app.domain.run import EvaluationRun
from app.domain.score import ScoringPolicy
from app.regression.engine import RegressionEngine
from app.reports.service import ReportService
from app.repositories.evaluation_repository import EvaluationRepository
from app.repositories.score_repository import ScoreRepository
from app.scoring.engine import ScoreEngine


def test_regression_threshold_boundary_cases() -> None:
    """Test regression threshold boundary behaviors (-0.049 vs -0.050 vs -0.051)."""
    policy = ScoringPolicy(regression_threshold=0.05)
    score_engine = ScoreEngine(policy)
    reg_engine = RegressionEngine(policy)

    # Baseline: quality = 1.0
    b_eval = EvaluationRun(run_id="b1", total_cases=1, passed_cases=1, results=[
        EvaluationResult(test_id="q1", evaluator="AccuracyEvaluator", passed=True, score=1.0, reason="pass")
    ])
    b_score = score_engine.calculate_run_score("b1", "demorrag", eval_run=b_eval)

    # Case 1: Candidate quality = 0.951 (delta = -0.049) -> NO REGRESSION
    c1_eval = EvaluationRun(run_id="c1", total_cases=1, passed_cases=1, results=[
        EvaluationResult(test_id="q1", evaluator="AccuracyEvaluator", passed=True, score=0.951, reason="pass")
    ])
    c1_score = score_engine.calculate_run_score("c1", "demorrag", eval_run=c1_eval)
    reg1 = reg_engine.compare_scores(b_score, c1_score, baseline_eval_run=b_eval, candidate_eval_run=c1_eval)
    assert reg1.detected is False

    # Case 2: Candidate quality = 0.950 (delta = -0.050) -> REGRESSION DETECTED
    c2_eval = EvaluationRun(run_id="c2", total_cases=1, passed_cases=1, results=[
        EvaluationResult(test_id="q1", evaluator="AccuracyEvaluator", passed=True, score=0.950, reason="pass")
    ])
    c2_score = score_engine.calculate_run_score("c2", "demorrag", eval_run=c2_eval)
    reg2 = reg_engine.compare_scores(b_score, c2_score, baseline_eval_run=b_eval, candidate_eval_run=c2_eval)
    assert reg2.detected is True

    # Case 3: Candidate quality = 0.949 (delta = -0.051) -> REGRESSION DETECTED
    c3_eval = EvaluationRun(run_id="c3", total_cases=1, passed_cases=1, results=[
        EvaluationResult(test_id="q1", evaluator="AccuracyEvaluator", passed=True, score=0.949, reason="pass")
    ])
    c3_score = score_engine.calculate_run_score("c3", "demorrag", eval_run=c3_eval)
    reg3 = reg_engine.compare_scores(b_score, c3_score, baseline_eval_run=b_eval, candidate_eval_run=c3_eval)
    assert reg3.detected is True


def test_missing_data_na_safety(isolated_db) -> None:
    """Test that missing security or quality tests display N/A rather than fictitious 100% scores."""
    db = isolated_db
    eval_repo = EvaluationRepository(db)
    score_repo = ScoreRepository(db)
    score_engine = ScoreEngine()

    # Create Quality-only run
    eval_run = EvaluationRun(
        run_id="q_only_run",
        target="demorrag",
        total_cases=1,
        passed_cases=1,
        results=[
            EvaluationResult(test_id="q1", evaluator="AccuracyEvaluator", passed=True, score=0.8, reason="pass")
        ],
    )
    eval_repo.save_run(eval_run)
    q_score = score_engine.calculate_run_score("q_only_run", "demorrag", eval_run=eval_run)
    score_repo.save_score(q_score)

    report_svc = ReportService(db)
    report = report_svc.generate_run_report("q_only_run")

    # Quality available, Security NOT available (N/A)
    assert report.quality.available is True
    assert report.quality.quality_score == 0.8
    assert report.security.available is False
    assert report.security.security_score is None


def test_failure_transition_classifications() -> None:
    """Test failure change classifications: new_failure, fixed_failure, persistent_failure."""
    policy = ScoringPolicy()
    reg_engine = RegressionEngine(policy)
    score_engine = ScoreEngine(policy)

    b_eval = EvaluationRun(run_id="b", results=[
        EvaluationResult(test_id="t1", evaluator="Accuracy", passed=False, score=0.0, reason="fail"),
        EvaluationResult(test_id="t2", evaluator="Relevance", passed=True, score=1.0, reason="pass"),
    ])
    c_eval = EvaluationRun(run_id="c", results=[
        EvaluationResult(test_id="t1", evaluator="Accuracy", passed=True, score=1.0, reason="pass"),  # Fixed
        EvaluationResult(test_id="t2", evaluator="Relevance", passed=False, score=0.0, reason="fail"), # New
    ])

    b_score = score_engine.calculate_run_score("b", "mock", eval_run=b_eval)
    c_score = score_engine.calculate_run_score("c", "mock", eval_run=c_eval)

    res = reg_engine.compare_scores(b_score, c_score, baseline_eval_run=b_eval, candidate_eval_run=c_eval)

    assert len(res.comparison.new_failures) == 1
    assert res.comparison.new_failures[0].test_id == "t2"
    assert len(res.comparison.fixed_failures) == 1
    assert res.comparison.fixed_failures[0].test_id == "t1"
