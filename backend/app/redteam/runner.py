import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from app.core.logging import logger
from app.domain.case import EvaluationCase
from app.domain.redteam import RedTeamCase, RedTeamResult, RedTeamRun, Severity
from app.domain.target import TargetAdapter
from app.redteam.evaluators.registry import get_redteam_evaluator


class RedTeamRunner:
    """Orchestrates adversarial attack cases execution against target adapters and evaluates defenses."""

    def __init__(self, target_adapter: TargetAdapter) -> None:
        self.target_adapter = target_adapter

    def run(
        self,
        cases: Sequence[RedTeamCase],
        target_name: str = "demorrag",
        run_id: str | None = None,
    ) -> RedTeamRun:
        """Run all attack cases through the target adapter and red-team evaluators, producing a RedTeamRun."""
        actual_run_id = run_id or f"rt_{uuid.uuid4().hex[:8]}"
        started_at = datetime.now(UTC)

        run_record = RedTeamRun(
            run_id=actual_run_id,
            target=target_name,
            started_at=started_at,
            status="running",
            total_cases=len(cases),
        )

        all_results: list[RedTeamResult] = []
        passed_cases_count = 0
        failed_cases_count = 0
        high_critical_failures_count = 0

        logger.info(f"Starting Red-Team run '{actual_run_id}' with {len(cases)} attack cases against target '{target_name}'...")

        try:
            for case in cases:
                # 1. Convert RedTeamCase attack prompt to EvaluationCase
                eval_case = EvaluationCase(
                    id=case.id,
                    input=case.attack,
                    category=case.category.value,
                    tags=case.tags,
                    metadata=case.metadata,
                )

                # 2. Execute attack against target adapter
                target_response = self.target_adapter.run(eval_case)

                # 3. Resolve and run red-team evaluator
                evaluator = get_redteam_evaluator(case.category)
                result = evaluator.evaluate(case, target_response)
                all_results.append(result)

                if result.passed:
                    passed_cases_count += 1
                else:
                    failed_cases_count += 1
                    if result.severity in [Severity.HIGH, Severity.CRITICAL]:
                        high_critical_failures_count += 1

            completed_at = datetime.now(UTC)
            run_record.completed_at = completed_at
            run_record.status = "completed"
            run_record.total_cases = len(cases)
            run_record.passed_cases = passed_cases_count
            run_record.failed_cases = failed_cases_count
            run_record.high_critical_failures = high_critical_failures_count
            run_record.results = all_results

            logger.info(
                f"Completed Red-Team run '{actual_run_id}': {passed_cases_count}/{len(cases)} defended, {failed_cases_count} failed."
            )
            return run_record

        except Exception as e:  # noqa: BLE001
            logger.error(f"Execution error in Red-Team run '{actual_run_id}': {e}")
            run_record.completed_at = datetime.now(UTC)
            run_record.status = "failed"
            run_record.results = all_results
            return run_record
