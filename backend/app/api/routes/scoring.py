from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.domain.regression import RegressionResult
from app.domain.score import RunScore
from app.regression.engine import RegressionEngine
from app.repositories.evaluation_repository import EvaluationRepository
from app.repositories.redteam_repository import RedTeamRepository
from app.repositories.score_repository import ScoreRepository
from app.scoring.engine import ScoreEngine

router = APIRouter()


@router.get("/evaluations/{run_id}/score", response_model=RunScore)
def get_run_score(
    run_id: str,
    db: Session = Depends(get_db),
) -> RunScore:
    """Retrieve or calculate Quality, Security, and Overall Reliability scores for a run."""
    score_repo = ScoreRepository(db)
    score = score_repo.get_score(run_id)

    if not score:
        eval_repo = EvaluationRepository(db)
        rt_repo = RedTeamRepository(db)

        eval_run = eval_repo.get_run_by_id(run_id)
        rt_run = rt_repo.get_run(run_id)

        if not eval_run and not rt_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Run with ID '{run_id}' not found.",
            )

        engine = ScoreEngine()
        target = eval_run.target if eval_run else (rt_run.target if rt_run else "demorrag")
        score = engine.calculate_run_score(
            run_id=run_id,
            target=target,
            eval_run=eval_run,
            redteam_run=rt_run,
        )
        score_repo.save_score(score)

    return score


@router.get("/evaluations/compare/{baseline_id}/{candidate_id}", response_model=RegressionResult)
def compare_runs(
    baseline_id: str,
    candidate_id: str,
    db: Session = Depends(get_db),
) -> RegressionResult:
    """Compare baseline and candidate evaluation runs and return regression analysis report."""
    score_repo = ScoreRepository(db)
    eval_repo = EvaluationRepository(db)
    rt_repo = RedTeamRepository(db)
    engine = ScoreEngine()
    reg_engine = RegressionEngine()

    def _get_or_calc(run_id: str):
        s = score_repo.get_score(run_id)
        e_run = eval_repo.get_run_by_id(run_id)
        rt_run = rt_repo.get_run(run_id)
        if not s and (e_run or rt_run):
            target = e_run.target if e_run else (rt_run.target if rt_run else "demorrag")
            s = engine.calculate_run_score(run_id=run_id, target=target, eval_run=e_run, redteam_run=rt_run)
            score_repo.save_score(s)
        return s, e_run, rt_run

    b_score, b_eval, b_rt = _get_or_calc(baseline_id)
    c_score, c_eval, c_rt = _get_or_calc(candidate_id)

    if not b_score or not c_score:
        missing = baseline_id if not b_score else candidate_id
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run ID '{missing}' not found for comparison.",
        )

    return reg_engine.compare_scores(
        baseline_score=b_score,
        candidate_score=c_score,
        baseline_eval_run=b_eval,
        candidate_eval_run=c_eval,
        baseline_redteam_run=b_rt,
        candidate_redteam_run=c_rt,
    )
