import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import RunScoreModel
from app.domain.score import OverallScore, QualityScore, RunScore, ScoringPolicy, SecurityScore


class ScoreRepository:
    """Repository for persisting and retrieving RunScore records."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def save_score(self, score: RunScore) -> RunScore:
        """Save or update a RunScore record."""
        stmt = select(RunScoreModel).where(RunScoreModel.run_id == score.run_id)
        existing = self.db.scalar(stmt)

        metrics_payload = {
            "quality": score.quality_score.model_dump(),
            "security": score.security_score.model_dump(),
            "overall": score.overall_score.model_dump(),
        }

        if existing:
            existing.quality_score = score.quality_score.score
            existing.security_score = score.security_score.score
            existing.overall_score = score.overall_score.score
            existing.policy_json = json.dumps(score.scoring_policy.model_dump())
            existing.metrics_json = json.dumps(metrics_payload)
        else:
            model = RunScoreModel(
                run_id=score.run_id,
                target=score.target,
                quality_score=score.quality_score.score,
                security_score=score.security_score.score,
                overall_score=score.overall_score.score,
                policy_json=json.dumps(score.scoring_policy.model_dump()),
                metrics_json=json.dumps(metrics_payload),
                created_at=score.created_at,
            )
            self.db.add(model)

        self.db.commit()
        return score

    def get_score(self, run_id: str) -> RunScore | None:
        """Retrieve a RunScore record by run_id."""
        stmt = select(RunScoreModel).where(RunScoreModel.run_id == run_id)
        model = self.db.scalar(stmt)
        if not model:
            return None

        policy_dict = json.loads(model.policy_json)
        metrics_dict = json.loads(model.metrics_json)

        return RunScore(
            run_id=model.run_id,
            target=model.target,
            created_at=model.created_at,
            quality_score=QualityScore.model_validate(metrics_dict["quality"]),
            security_score=SecurityScore.model_validate(metrics_dict["security"]),
            overall_score=OverallScore.model_validate(metrics_dict["overall"]),
            scoring_policy=ScoringPolicy.model_validate(policy_dict),
        )
