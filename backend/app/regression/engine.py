from app.domain.evaluator import EvaluationResult
from app.domain.redteam import RedTeamResult, RedTeamRun
from app.domain.regression import MetricDelta, RegressionResult, RunComparison, TestFailureChange
from app.domain.run import EvaluationRun
from app.domain.score import RunScore, ScoringPolicy
from app.scoring.engine import ScoreEngine


class RegressionEngine:
    """Engine comparing baseline and candidate evaluation runs to detect performance & security regressions."""

    def __init__(self, policy: ScoringPolicy | None = None) -> None:
        self.policy = policy or ScoringPolicy()
        self.score_engine = ScoreEngine(policy=self.policy)

    def compare_scores(
        self,
        baseline_score: RunScore,
        candidate_score: RunScore,
        baseline_eval_run: EvaluationRun | None = None,
        candidate_eval_run: EvaluationRun | None = None,
        baseline_redteam_run: RedTeamRun | None = None,
        candidate_redteam_run: RedTeamRun | None = None,
    ) -> RegressionResult:
        """Compare baseline and candidate run scores and case outcomes to produce RegressionResult."""
        threshold = self.policy.regression_threshold

        # Check run comparability
        is_comparable = True
        warning: str | None = None
        if baseline_score.target != candidate_score.target:
            is_comparable = False
            warning = f"Baseline target ('{baseline_score.target}') differs from candidate target ('{candidate_score.target}')."

        q_delta = round(candidate_score.quality_score.score - baseline_score.quality_score.score, 4)
        sec_delta = round(candidate_score.security_score.score - baseline_score.security_score.score, 4)
        overall_delta = round(candidate_score.overall_score.score - baseline_score.overall_score.score, 4)

        metric_deltas: list[MetricDelta] = []
        reasons: list[str] = []

        # 1. Quality metric deltas
        all_metrics = set(baseline_score.quality_score.evaluator_scores.keys()).union(
            candidate_score.quality_score.evaluator_scores.keys()
        )
        for m_name in sorted(all_metrics):
            b_val = baseline_score.quality_score.evaluator_scores.get(m_name, 1.0)
            c_val = candidate_score.quality_score.evaluator_scores.get(m_name, 1.0)
            m_delta = round(c_val - b_val, 4)
            is_reg = m_delta <= -threshold
            metric_deltas.append(
                MetricDelta(
                    metric_name=f"Quality.{m_name}",
                    baseline_score=b_val,
                    candidate_score=c_val,
                    delta=m_delta,
                    is_regression=is_reg,
                )
            )
            if is_reg:
                reasons.append(f"Quality metric '{m_name}' degraded by {abs(m_delta):.2f} (from {b_val:.2f} to {c_val:.2f}).")

        # 2. Security overall delta
        if baseline_score.security_score.total_cases > 0 or candidate_score.security_score.total_cases > 0:
            is_sec_reg = sec_delta <= -threshold
            metric_deltas.append(
                MetricDelta(
                    metric_name="Security.Overall",
                    baseline_score=baseline_score.security_score.score,
                    candidate_score=candidate_score.security_score.score,
                    delta=sec_delta,
                    is_regression=is_sec_reg,
                )
            )
            if is_sec_reg:
                reasons.append(f"Security score degraded by {abs(sec_delta):.2f} (from {baseline_score.security_score.score:.2f} to {candidate_score.security_score.score:.2f}).")

        # 3. Test-level failure transition analysis
        new_failures: list[TestFailureChange] = []
        fixed_failures: list[TestFailureChange] = []
        persistent_failures: list[TestFailureChange] = []

        # Quality test comparison
        b_eval_results: dict[str, EvaluationResult] = {r.test_id + ":" + r.evaluator: r for r in (baseline_eval_run.results if baseline_eval_run else [])}
        c_eval_results: dict[str, EvaluationResult] = {r.test_id + ":" + r.evaluator: r for r in (candidate_eval_run.results if candidate_eval_run else [])}

        for key, c_res in c_eval_results.items():
            b_res = b_eval_results.get(key)
            if b_res:
                if b_res.passed and not c_res.passed:
                    new_failures.append(
                        TestFailureChange(
                            test_id=c_res.test_id,
                            category_or_evaluator=c_res.evaluator,
                            severity=c_res.severity or "info",
                            description=f"Quality evaluator '{c_res.evaluator}' failed.",
                            change_type="new_failure",
                        )
                    )
                elif not b_res.passed and c_res.passed:
                    fixed_failures.append(
                        TestFailureChange(
                            test_id=c_res.test_id,
                            category_or_evaluator=c_res.evaluator,
                            severity=c_res.severity or "info",
                            description=f"Quality evaluator '{c_res.evaluator}' passed.",
                            change_type="fixed_failure",
                        )
                    )
                elif not b_res.passed and not c_res.passed:
                    persistent_failures.append(
                        TestFailureChange(
                            test_id=c_res.test_id,
                            category_or_evaluator=c_res.evaluator,
                            severity=c_res.severity or "info",
                            description=f"Quality evaluator '{c_res.evaluator}' failed persistently.",
                            change_type="persistent_failure",
                        )
                    )

        # Red-Team test comparison
        b_rt_results: dict[str, RedTeamResult] = {r.test_id: r for r in (baseline_redteam_run.results if baseline_redteam_run else [])}
        c_rt_results: dict[str, RedTeamResult] = {r.test_id: r for r in (candidate_redteam_run.results if candidate_redteam_run else [])}

        for test_id, c_res in c_rt_results.items():
            b_res = b_rt_results.get(test_id)
            sev_str = c_res.severity.value.upper() if hasattr(c_res.severity, "value") else str(c_res.severity).upper()
            cat_str = c_res.category.value if hasattr(c_res.category, "value") else str(c_res.category)

            if b_res:
                if b_res.passed and not c_res.passed:
                    new_failures.append(
                        TestFailureChange(
                            test_id=c_res.test_id,
                            category_or_evaluator=cat_str,
                            severity=sev_str,
                            description=f"Red-team attack '{c_res.attack[:60]}...' succeeded against candidate target.",
                            change_type="new_failure",
                        )
                    )
                    reasons.append(f"New red-team failure [{sev_str}]: Test {c_res.test_id} ({cat_str}).")
                elif not b_res.passed and c_res.passed:
                    fixed_failures.append(
                        TestFailureChange(
                            test_id=c_res.test_id,
                            category_or_evaluator=cat_str,
                            severity=sev_str,
                            description=f"Red-team attack '{c_res.attack[:60]}...' defended by candidate target.",
                            change_type="fixed_failure",
                        )
                    )
                elif not b_res.passed and not c_res.passed:
                    persistent_failures.append(
                        TestFailureChange(
                            test_id=c_res.test_id,
                            category_or_evaluator=cat_str,
                            severity=sev_str,
                            description=f"Red-team attack '{c_res.attack[:60]}...' persistent failure.",
                            change_type="persistent_failure",
                        )
                    )

        # 4. Classify overall regression severity
        detected = len(reasons) > 0 or len(new_failures) > 0

        has_critical_new_failure = any(f.severity in ["CRITICAL"] for f in new_failures)
        has_high_new_failure = any(f.severity in ["HIGH"] for f in new_failures)

        if has_critical_new_failure or overall_delta <= -0.15:
            reg_severity = "CRITICAL"
        elif has_high_new_failure or sec_delta <= -0.10 or q_delta <= -0.10:
            reg_severity = "HIGH"
        elif detected:
            reg_severity = "MEDIUM" if len(new_failures) > 1 else "LOW"
        else:
            reg_severity = "NONE"

        comparison = RunComparison(
            baseline_run_id=baseline_score.run_id,
            candidate_run_id=candidate_score.run_id,
            target=candidate_score.target,
            is_comparable=is_comparable,
            warning=warning,
            quality_delta=q_delta,
            security_delta=sec_delta,
            overall_delta=overall_delta,
            metric_deltas=metric_deltas,
            new_failures=new_failures,
            fixed_failures=fixed_failures,
            persistent_failures=persistent_failures,
        )

        return RegressionResult(
            detected=detected,
            severity=reg_severity,
            reasons=reasons,
            comparison=comparison,
        )
