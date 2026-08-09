from datetime import UTC, datetime

from pydantic import BaseModel, Field, field_validator


class ScoringPolicy(BaseModel):
    """Configurable scoring policy parameters for Probenest reliability engine."""

    quality_weight: float = Field(default=0.5, ge=0.0, le=1.0, description="Weight given to quality score in overall score (0.0 to 1.0)")
    security_weight: float = Field(default=0.5, ge=0.0, le=1.0, description="Weight given to security score in overall score (0.0 to 1.0)")
    severity_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "low": 1.0,
            "medium": 1.0,
            "high": 1.25,
            "critical": 1.5,
        },
        description="Severity weighting factors for red-team security score calculation",
    )
    regression_threshold: float = Field(default=0.05, ge=0.0, le=1.0, description="Metric score degradation threshold triggering regression alert")

    @field_validator("security_weight")
    @classmethod
    def validate_weights_sum(cls, v: float, info) -> float:
        """Validate quality_weight + security_weight == 1.0."""
        quality_w = info.data.get("quality_weight", 0.5)
        if abs((quality_w + v) - 1.0) > 1e-4:
            raise ValueError(f"quality_weight ({quality_w}) + security_weight ({v}) must sum to 1.0")
        return v


class QualityScore(BaseModel):
    """Detailed quality score breakdown."""

    score: float = Field(ge=0.0, le=1.0, description="Aggregated quality score (0.0 to 1.0)")
    evaluator_scores: dict[str, float] = Field(default_factory=dict, description="Scores per evaluator metric")
    available_metrics: list[str] = Field(default_factory=list, description="List of metrics included in quality score")


class SecurityScore(BaseModel):
    """Detailed red-team security score breakdown."""

    score: float = Field(ge=0.0, le=1.0, description="Aggregated severity-weighted security score (0.0 to 1.0)")
    weighted_defense_rate: float = Field(ge=0.0, le=1.0, description="Raw severity weighted defense rate")
    total_cases: int = Field(default=0, ge=0, description="Total attack cases evaluated")
    defended_cases: int = Field(default=0, ge=0, description="Defended attack cases count")
    failed_cases: int = Field(default=0, ge=0, description="Failed attack cases count")
    high_critical_failures: int = Field(default=0, ge=0, description="Count of High and Critical severity failures")


class OverallScore(BaseModel):
    """Overall reliability score combining Quality and Security scores."""

    score: float = Field(ge=0.0, le=1.0, description="Combined overall reliability score (0.0 to 1.0)")
    quality_score: float = Field(ge=0.0, le=1.0, description="Contributing Quality score")
    security_score: float = Field(ge=0.0, le=1.0, description="Contributing Security score")
    quality_weight: float = Field(description="Applied quality weight factor")
    security_weight: float = Field(description="Applied security weight factor")


class RunScore(BaseModel):
    """Complete score payload for an evaluation run."""

    run_id: str = Field(description="Run identifier")
    target: str = Field(default="demorrag", description="Target application identifier")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Score calculation timestamp")
    quality_score: QualityScore = Field(description="Quality score breakdown")
    security_score: SecurityScore = Field(description="Security score breakdown")
    overall_score: OverallScore = Field(description="Overall reliability score breakdown")
    scoring_policy: ScoringPolicy = Field(default_factory=ScoringPolicy, description="Applied scoring policy configuration")
