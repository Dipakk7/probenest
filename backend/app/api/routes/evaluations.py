from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.adapters.demo_rag import DemoRAGAdapter
from app.adapters.mock_target import MockTargetAdapter
from app.db.database import get_db
from app.domain.run import EvaluationRun
from app.evaluators.registry import get_evaluators_by_names
from app.loaders.dataset import DatasetLoadError
from app.services.evaluation_service import EvaluationService

router = APIRouter()


class TriggerEvaluationRequest(BaseModel):
    """Payload for triggering a new evaluation run."""

    target: str = Field(default="mock", description="Target application identifier ('mock' or 'demorrag')")
    dataset_path: str | None = Field(
        default=None,
        description="Path to evaluation dataset JSON file. Defaults to golden dataset.",
    )
    evaluators: list[str] | None = Field(
        default=None,
        description="List of requested evaluator metric names (e.g. ['accuracy', 'relevance', 'faithfulness', 'hallucination'])",
    )


def _resolve_default_dataset(target: str) -> Path:
    """Resolve absolute path to golden dataset."""
    current_file = Path(__file__).resolve()
    repo_root = current_file.parents[4]
    filename = "rag.json" if target.lower() in ["demorrag", "rag"] else "example.json"
    dataset_path = repo_root / "datasets" / "golden" / filename
    if not dataset_path.is_file():
        alt_path = Path(f"datasets/golden/{filename}").resolve()
        if alt_path.is_file():
            return alt_path
    return dataset_path


@router.post("/evaluations", response_model=EvaluationRun, status_code=status.HTTP_201_CREATED)
def trigger_evaluation(
    payload: TriggerEvaluationRequest | None = None,
    db: Session = Depends(get_db),
) -> EvaluationRun:
    """Trigger a new evaluation run against the target application with quality evaluators."""
    target_name = payload.target if payload and payload.target else "mock"
    if target_name.lower() in ["demorrag", "rag"]:
        adapter = DemoRAGAdapter()
    else:
        adapter = MockTargetAdapter()

    if payload and payload.dataset_path:
        dataset_file = payload.dataset_path
    else:
        dataset_file = str(_resolve_default_dataset(target_name))

    requested_eval_names = payload.evaluators if payload and payload.evaluators else ["quality"]
    evaluator_instances = get_evaluators_by_names(requested_eval_names)

    service = EvaluationService(db)
    try:
        run = service.run_evaluation(
            dataset_path_or_cases=dataset_file,
            target_adapter=adapter,
            evaluators=evaluator_instances,
        )
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
