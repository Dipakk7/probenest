import pytest

from app.domain.evaluator import EvaluationResult
from app.domain.redteam import AttackCategory, RedTeamResult, Severity
from app.domain.score import ScoringPolicy
from app.scoring.engine import ScoreEngine


def test_scoring_policy_validation() -> None:
    """Test ScoringPolicy quality and security weights sum to 1.0."""
    policy = ScoringPolicy(quality_weight=0.6, security_weight=0.4)
    assert policy.quality_weight == 0.6
    assert policy.security_weight == 0.4

    with pytest.raises(ValueError, match="must sum to 1.0"):
        ScoringPolicy(quality_weight=0.8, security_weight=0.5)


def test_quality_score_calculation() -> None:
    """Test QualityScore calculation mean logic."""
    engine = ScoreEngine()
    results = [
        EvaluationResult(test_id="t1", evaluator="AccuracyEvaluator", passed=True, score=1.0, reason="pass"),
        EvaluationResult(test_id="t2", evaluator="AccuracyEvaluator", passed=True, score=0.8, reason="pass"),
        EvaluationResult(test_id="t1", evaluator="RelevanceEvaluator", passed=True, score=1.0, reason="pass"),
    ]

    q_score = engine.calculate_quality_score(results)
    assert q_score.score == 0.95  # Accuracy avg=0.9, Relevance avg=1.0 -> mean = 0.95
    assert q_score.evaluator_scores["Accuracy"] == 0.9
    assert q_score.evaluator_scores["Relevance"] == 1.0


def test_security_score_severity_weighting() -> None:
    """Test SecurityScore severity weighting calculation."""
    engine = ScoreEngine()
    results = [
        RedTeamResult(
            test_id="SEC-01",
            category=AttackCategory.PROMPT_INJECTION,
            attack="a1",
            passed=True,
            severity=Severity.LOW,
            reason="pass",
            actual_output="out",
            expected_behavior="refuse",
        ),
        RedTeamResult(
            test_id="SEC-02",
            category=AttackCategory.JAILBREAK,
            attack="a2",
            passed=False,
            severity=Severity.CRITICAL,
            reason="fail",
            actual_output="out",
            expected_behavior="refuse",
        ),
    ]

    # Low weight = 1.0 (pass), Critical weight = 1.5 (fail). Total = 2.5, Defended = 1.0. Rate = 1.0/2.5 = 0.4
    sec_score = engine.calculate_security_score(results)
    assert sec_score.score == 0.4
    assert sec_score.high_critical_failures == 1


def test_overall_run_score() -> None:
    """Test overall score combined quality and security weights."""
    engine = ScoreEngine(ScoringPolicy(quality_weight=0.5, security_weight=0.5))

    q_results = [EvaluationResult(test_id="t1", evaluator="AccuracyEvaluator", passed=True, score=0.8, reason="pass")]
    rt_results = [
        RedTeamResult(
            test_id="SEC-01",
            category=AttackCategory.PROMPT_INJECTION,
            attack="a1",
            passed=True,
            severity=Severity.LOW,
            reason="pass",
            actual_output="out",
            expected_behavior="refuse",
        )
    ]

    score = engine.calculate_run_score("run_test", "mock", quality_results=q_results, redteam_results=rt_results)
    assert score.quality_score.score == 0.8
    assert score.security_score.score == 1.0
    assert score.overall_score.score == 0.9  # (0.8*0.5 + 1.0*0.5)
