import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from app.core.logging import logger
from app.domain.case import EvaluationCase
from app.domain.evaluator import EvaluationResult, Evaluator
from app.domain.run import EvaluationRun, RunStatus
from app.domain.target import TargetAdapter


class EvaluationRunner:
    """Orchestrates evaluation cases execution against target adapters and evaluates results generically."""

    def __init__(self, target_adapter: TargetAdapter, evaluators: Sequence[Evaluator]) -> None:
        self.target_adapter = target_adapter
        self.evaluators = evaluators

    def run(self, cases: Sequence[EvaluationCase], run_id: str | None = None) -> EvaluationRun:
        """Run all cases through the target adapter and evaluators, producing an EvaluationRun."""
        actual_run_id = run_id or f"run_{uuid.uuid4().hex[:8]}"
        started_at = datetime.now(UTC)

        run_record = EvaluationRun(
            run_id=actual_run_id,
            started_at=started_at,
            status=RunStatus.RUNNING,
            total_cases=len(cases),
        )

        all_results: list[EvaluationResult] = []
        passed_cases_count = 0
        failed_cases_count = 0

        logger.info(f"Starting evaluation run '{actual_run_id}' with {len(cases)} cases...")

        try:
            for case in cases:
                # 1. Execute case against target adapter
                target_response = self.target_adapter.run(case)

                # 2. Run generic evaluators
                case_passed = True
                for evaluator in self.evaluators:
                    result = evaluator.evaluate(case, target_response)
                    all_results.append(result)

                    if not result.passed:
                        case_passed = False

                if case_passed:
                    passed_cases_count += 1
                else:
                    failed_cases_count += 1

            completed_at = datetime.now(UTC)
            run_record.completed_at = completed_at
            run_record.status = RunStatus.COMPLETED
            run_record.total_cases = len(cases)
            run_record.passed_cases = passed_cases_count
            run_record.failed_cases = failed_cases_count
            run_record.results = all_results

            logger.info(
                f"Completed run '{actual_run_id}': {passed_cases_count}/{len(cases)} passed, {failed_cases_count} failed."
            )
            return run_record

        except Exception as e:  # noqa: BLE001
            logger.error(f"Execution error in run '{actual_run_id}': {e}")
            run_record.completed_at = datetime.now(UTC)
            run_record.status = RunStatus.FAILED
            run_record.results = all_results
            return run_record
