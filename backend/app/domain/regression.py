from pydantic import BaseModel, Field


class MetricDelta(BaseModel):
    """Comparison metric delta between baseline and candidate runs."""

    metric_name: str = Field(description="Name of the metric or evaluator")
    baseline_score: float = Field(description="Baseline run score (0.0 to 1.0)")
    candidate_score: float = Field(description="Candidate run score (0.0 to 1.0)")
    delta: float = Field(description="Absolute score change (candidate - baseline)")
    is_regression: bool = Field(description="True if degradation exceeds regression threshold")


class TestFailureChange(BaseModel):
    """Represents a test-level failure transition between baseline and candidate runs."""

    test_id: str = Field(description="Test case identifier")
    category_or_evaluator: str = Field(description="Category or evaluator name")
    severity: str = Field(description="Severity rating of the case")
    description: str = Field(description="Attack prompt or test case input summary")
    change_type: str = Field(description="Transition type: 'new_failure', 'fixed_failure', or 'persistent_failure'")


class RunComparison(BaseModel):
    """Run-to-run comparison container."""

    baseline_run_id: str = Field(description="Baseline run identifier")
    candidate_run_id: str = Field(description="Candidate run identifier")
    target: str = Field(description="Target application name")
    is_comparable: bool = Field(default=True, description="True if baseline and candidate runs are logically comparable")
    warning: str | None = Field(default=None, description="Warning explanation if runs differ in target or dataset")
    quality_delta: float = Field(description="Quality score change (candidate - baseline)")
    security_delta: float = Field(description="Security score change (candidate - baseline)")
    overall_delta: float = Field(description="Overall reliability score change (candidate - baseline)")
    metric_deltas: list[MetricDelta] = Field(default_factory=list, description="Individual metric deltas")
    new_failures: list[TestFailureChange] = Field(default_factory=list, description="New failures introduced in candidate run")
    fixed_failures: list[TestFailureChange] = Field(default_factory=list, description="Failures resolved in candidate run")
    persistent_failures: list[TestFailureChange] = Field(default_factory=list, description="Failures present in both runs")


class RegressionResult(BaseModel):
    """Overall regression detection outcome."""

    detected: bool = Field(description="True if one or more regressions were detected")
    severity: str = Field(description="Regression severity rating ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'NONE')")
    reasons: list[str] = Field(default_factory=list, description="List of justifications for detected regression")
    comparison: RunComparison = Field(description="Underlying run comparison report")
