from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.domain.run import EvaluationRun
from app.loaders.dataset import DatasetLoadError
from app.services.evaluation_service import EvaluationService

router = APIRouter()


class TriggerEvaluationRequest(BaseModel):
    """Payload for triggering a new evaluation run."""

    dataset_path: str | None = Field(
        default=None,
        description="Path to evaluation dataset JSON file. Defaults to sample golden dataset.",
    )


def _resolve_default_dataset() -> Path:
    """Resolve absolute path to golden example dataset."""
    current_file = Path(__file__).resolve()
    # Go up: routes -> api -> app -> backend -> probenest root
    repo_root = current_file.parents[4]
    dataset_path = repo_root / "datasets" / "golden" / "example.json"
    if not dataset_path.is_file():
        # Fallback relative search
        alt_path = Path("datasets/golden/example.json").resolve()
        if alt_path.is_file():
            return alt_path
    return dataset_path


@router.post("/evaluations", response_model=EvaluationRun, status_code=status.HTTP_201_CREATED)
def trigger_evaluation(
    payload: TriggerEvaluationRequest | None = None,
    db: Session = Depends(get_db),
) -> EvaluationRun:
    """Trigger a new evaluation run against the mock target with exact match evaluator."""
    if payload and payload.dataset_path:
        dataset_file = payload.dataset_path
    else:
        dataset_file = str(_resolve_default_dataset())

    service = EvaluationService(db)
    try:
        run = service.run_evaluation(dataset_path_or_cases=dataset_file)
        return run
    except DatasetLoadError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to load dataset: {e}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {e}",
        ) from e


@router.get("/evaluations", response_model=list[EvaluationRun])
def list_evaluations(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[EvaluationRun]:
    """Retrieve historical evaluation runs."""
    service = EvaluationService(db)
    return service.list_runs(limit=limit, offset=offset)


@router.get("/evaluations/{run_id}", response_model=EvaluationRun)
def get_evaluation(
    run_id: str,
    db: Session = Depends(get_db),
) -> EvaluationRun:
    """Retrieve details and case results for a specific evaluation run."""
    service = EvaluationService(db)
    run = service.get_run(run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation run with ID '{run_id}' not found.",
        )
    return run
