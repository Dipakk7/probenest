from typing import Protocol, runtime_checkable

from app.domain.redteam import RedTeamCase, RedTeamResult
from app.domain.target import TargetResponse


@runtime_checkable
class RedTeamEvaluator(Protocol):
    """Protocol interface for adversarial red-team evaluators."""

    name: str

    def evaluate(self, case: RedTeamCase, response: TargetResponse) -> RedTeamResult:
        """Evaluate target response against adversarial attack case.

        Returns:
            RedTeamResult: passed=True if target RESISTED attack, passed=False if target SUCCUMBED to attack.
        """
        ...
