from app.core.config import settings
from app.judges.base import EvaluationJudge
from app.judges.mock import MockEvaluationJudge
from app.judges.ollama import OllamaEvaluationJudge


def get_judge(provider: str | None = None) -> EvaluationJudge:
    """Factory function returning configured EvaluationJudge instance."""
    chosen_provider = (provider or settings.EVALUATION_JUDGE_PROVIDER).lower()

    if chosen_provider == "ollama":
        return OllamaEvaluationJudge(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.EVALUATION_JUDGE_MODEL,
        )

    return MockEvaluationJudge()
