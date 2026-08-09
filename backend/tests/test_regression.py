from app.domain.evaluator import EvaluationResult
from app.domain.redteam import AttackCategory, RedTeamResult, RedTeamRun, Severity
from app.domain.run import EvaluationRun
from app.domain.score import ScoringPolicy
from app.regression.engine import RegressionEngine
from app.scoring.engine import ScoreEngine


def test_regression_detection_delta_and_new_failures() -> None:
    """Test RegressionEngine detecting score degradation and new test failures."""
    policy = ScoringPolicy(regression_threshold=0.05)
    score_engine = ScoreEngine(policy)
    reg_engine = RegressionEngine(policy)

    # Baseline: 2/2 redteam passed, quality = 1.0
    b_eval = EvaluationRun(run_id="r1", total_cases=1, passed_cases=1, results=[
        EvaluationResult(test_id="q1", evaluator="AccuracyEvaluator", passed=True, score=1.0, reason="pass")
    ])
    b_rt = RedTeamRun(run_id="r1", total_cases=2, passed_cases=2, results=[
        RedTeamResult(test_id="SEC-01", category=AttackCategory.PROMPT_INJECTION, attack="a1", passed=True, severity=Severity.HIGH, reason="pass", actual_output="o", expected_behavior="e"),
        RedTeamResult(test_id="SEC-02", category=AttackCategory.JAILBREAK, attack="a2", passed=True, severity=Severity.CRITICAL, reason="pass", actual_output="o", expected_behavior="e"),
    ])
    b_score = score_engine.calculate_run_score("r1", "demorrag", eval_run=b_eval, redteam_run=b_rt)

    # Candidate: 1/2 redteam passed (SEC-02 newly failed), quality = 0.8
    c_eval = EvaluationRun(run_id="r2", total_cases=1, passed_cases=1, results=[
        EvaluationResult(test_id="q1", evaluator="AccuracyEvaluator", passed=True, score=0.8, reason="pass")
    ])
    c_rt = RedTeamRun(run_id="r2", total_cases=2, passed_cases=1, failed_cases=1, results=[
        RedTeamResult(test_id="SEC-01", category=AttackCategory.PROMPT_INJECTION, attack="a1", passed=True, severity=Severity.HIGH, reason="pass", actual_output="o", expected_behavior="e"),
        RedTeamResult(test_id="SEC-02", category=AttackCategory.JAILBREAK, attack="a2", passed=False, severity=Severity.CRITICAL, reason="fail", actual_output="o", expected_behavior="e"),
    ])
    c_score = score_engine.calculate_run_score("r2", "demorrag", eval_run=c_eval, redteam_run=c_rt)

    reg_result = reg_engine.compare_scores(
        baseline_score=b_score,
        candidate_score=c_score,
        baseline_eval_run=b_eval,
        candidate_eval_run=c_eval,
        baseline_redteam_run=b_rt,
        candidate_redteam_run=c_rt,
    )

    assert reg_result.detected is True
    assert reg_result.severity == "CRITICAL"  # Critical red-team test newly failed
    assert len(reg_result.comparison.new_failures) == 1
    assert reg_result.comparison.new_failures[0].test_id == "SEC-02"
    assert reg_result.comparison.quality_delta == -0.2
