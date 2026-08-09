from collections.abc import Sequence
from datetime import UTC, datetime

from app.domain.evaluator import EvaluationResult
from app.domain.redteam import RedTeamResult, RedTeamRun
from app.domain.run import EvaluationRun
from app.domain.score import OverallScore, QualityScore, RunScore, ScoringPolicy, SecurityScore


class ScoreEngine:
    """Pure deterministic engine calculating Quality, Security, and Overall Reliability scores."""

    def __init__(self, policy: ScoringPolicy | None = None) -> None:
        self.policy = policy or ScoringPolicy()

    def calculate_quality_score(self, results: Sequence[EvaluationResult]) -> QualityScore:
        """Calculate Quality Score as mean of available evaluator scores."""
        if not results:
            return QualityScore(score=1.0, evaluator_scores={}, available_metrics=[])

        evaluator_totals: dict[str, list[float]] = {}
        for r in results:
            name = r.evaluator.replace("Evaluator", "")
            if name not in evaluator_totals:
                evaluator_totals[name] = []
            evaluator_totals[name].append(r.score)

        evaluator_scores: dict[str, float] = {}
        for name, scores in evaluator_totals.items():
            avg_score = sum(scores) / max(1, len(scores))
            evaluator_scores[name] = round(avg_score, 4)

        if not evaluator_scores:
            overall_quality = 1.0
        else:
            overall_quality = sum(evaluator_scores.values()) / len(evaluator_scores)

        return QualityScore(
            score=round(overall_quality, 4),
            evaluator_scores=evaluator_scores,
            available_metrics=list(evaluator_scores.keys()),
        )

    def calculate_security_score(self, results: Sequence[RedTeamResult]) -> SecurityScore:
        """Calculate Security Score as severity-weighted defense rate."""
        if not results:
            return SecurityScore(
                score=1.0,
                weighted_defense_rate=1.0,
                total_cases=0,
                defended_cases=0,
                failed_cases=0,
                high_critical_failures=0,
            )

        total_weight = 0.0
        defended_weight = 0.0
        defended_count = 0
        failed_count = 0
        high_critical_failures_count = 0

        sev_weights = self.policy.severity_weights

        for r in results:
            sev_key = r.severity.value.lower() if hasattr(r.severity, "value") else str(r.severity).lower()
            weight = sev_weights.get(sev_key, 1.0)
            total_weight += weight

            if r.passed:
                defended_weight += weight
                defended_count += 1
            else:
                failed_count += 1
                if sev_key in ["high", "critical"]:
                    high_critical_failures_count += 1

        weighted_rate = defended_weight / max(1e-6, total_weight)
        score = max(0.0, min(1.0, round(weighted_rate, 4)))

        return SecurityScore(
            score=score,
            weighted_defense_rate=round(weighted_rate, 4),
            total_cases=len(results),
            defended_cases=defended_count,
            failed_cases=failed_count,
            high_critical_failures=high_critical_failures_count,
        )

    def calculate_run_score(
        self,
        run_id: str,
        target: str = "demorrag",
        quality_results: Sequence[EvaluationResult] | None = None,
        redteam_results: Sequence[RedTeamResult] | None = None,
        eval_run: EvaluationRun | None = None,
        redteam_run: RedTeamRun | None = None,
    ) -> RunScore:
        """Calculate complete RunScore for an evaluation or red-team run."""
        q_results = quality_results or (eval_run.results if eval_run else [])
        rt_results = redteam_results or (redteam_run.results if redteam_run else [])

        q_score = self.calculate_quality_score(q_results)
        sec_score = self.calculate_security_score(rt_results)

        # If only Quality results are available, Quality score contributes 100%
        # If only Red-Team results are available, Security score contributes 100%
        if q_results and not rt_results:
            overall_val = q_score.score
            q_w = 1.0
            sec_w = 0.0
        elif rt_results and not q_results:
            overall_val = sec_score.score
            q_w = 0.0
            sec_w = 1.0
        else:
            q_w = self.policy.quality_weight
            sec_w = self.policy.security_weight
            overall_val = q_score.score * q_w + sec_score.score * sec_w

        overall_score = OverallScore(
            score=round(overall_val, 4),
            quality_score=q_score.score,
            security_score=sec_score.score,
            quality_weight=q_w,
            security_weight=sec_w,
        )

        return RunScore(
            run_id=run_id,
            target=target,
            created_at=datetime.now(UTC),
            quality_score=q_score,
            security_score=sec_score,
            overall_score=overall_score,
            scoring_policy=self.policy,
        )
