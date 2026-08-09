"""Domain models and interfaces for Probenest evaluation core."""
from app.domain.case import EvaluationCase
from app.domain.evaluator import EvaluationResult, Evaluator
from app.domain.redteam import AttackCategory, RedTeamCase, RedTeamResult, RedTeamRun, Severity
from app.domain.regression import MetricDelta, RegressionResult, RunComparison, TestFailureChange
from app.domain.run import EvaluationRun, RunStatus
from app.domain.score import OverallScore, QualityScore, RunScore, ScoringPolicy, SecurityScore
from app.domain.target import TargetAdapter, TargetResponse

__all__ = [
    "AttackCategory",
    "EvaluationCase",
    "EvaluationResult",
    "EvaluationRun",
    "Evaluator",
    "MetricDelta",
    "OverallScore",
    "QualityScore",
    "RedTeamCase",
    "RedTeamResult",
    "RedTeamRun",
    "RegressionResult",
    "RunComparison",
    "RunScore",
    "RunStatus",
    "ScoringPolicy",
    "SecurityScore",
    "Severity",
    "TargetAdapter",
    "TargetResponse",
    "TestFailureChange",
]
