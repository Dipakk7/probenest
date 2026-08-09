from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.adapters.demo_rag import DemoRAGAdapter
from app.adapters.mock_target import MockTargetAdapter
from app.db.database import get_db
from app.domain.redteam import RedTeamCase, RedTeamRun
from app.loaders.dataset import DatasetLoadError
from app.loaders.redteam_loader import RedTeamDatasetLoader
from app.services.redteam_service import RedTeamService

router = APIRouter()


class TriggerRedTeamRequest(BaseModel):
    """Payload for triggering a new adversarial red-team run."""

    target: str = Field(default="demorrag", description="Target application identifier ('mock' or 'demorrag')")
    dataset_path: str | None = Field(
        default=None,
        description="Path to specific red-team attack dataset JSON file.",
    )
    category: str | None = Field(
        default=None,
        description="Specific attack category filter (e.g. 'prompt_injection', 'jailbreak', 'data_leakage')",
    )


def _load_all_redteam_cases() -> list[RedTeamCase]:
    """Load default red-team cases from datasets/redteam/ directory."""
    current_file = Path(__file__).resolve()
    repo_root = current_file.parents[4]
    redteam_dir = repo_root / "datasets" / "redteam"
    if not redteam_dir.is_dir():
        redteam_dir = Path("datasets/redteam").resolve()

    cases: list[RedTeamCase] = []
    dataset_files = ["injection.json", "jailbreak.json", "leakage.json", "tool_abuse.json"]
    for fname in dataset_files:
        fpath = redteam_dir / fname
        if fpath.is_file():
            cases.extend(RedTeamDatasetLoader.load_from_file(fpath))

    return cases


@router.post("/redteam", response_model=RedTeamRun, status_code=status.HTTP_201_CREATED)
def trigger_redteam(
    payload: TriggerRedTeamRequest | None = None,
    db: Session = Depends(get_db),
) -> RedTeamRun:
    """Trigger a new adversarial red-team test run against target application."""
    target_name = payload.target if payload and payload.target else "demorrag"
    if target_name.lower() in ["demorrag", "rag"]:
        adapter = DemoRAGAdapter()
    else:
        adapter = MockTargetAdapter()

    category_filter = payload.category if payload and payload.category else None

    if payload and payload.dataset_path:
        cases_source = payload.dataset_path
    else:
        cases_source = _load_all_redteam_cases()

    service = RedTeamService(db)
    try:
        run = service.run_redteam(
            dataset_path_or_cases=cases_source,
            target_adapter=adapter,
            target_name=target_name,
            category_filter=category_filter,
        )
        return run
    except DatasetLoadError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to load red-team dataset: {e}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Red-Team evaluation failed: {e}",
        ) from e


@router.get("/redteam", response_model=list[RedTeamRun])
def list_redteam_runs(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[RedTeamRun]:
    """Retrieve historical red-team runs."""
    service = RedTeamService(db)
    return service.list_runs(limit=limit, offset=offset)


@router.get("/redteam/{run_id}", response_model=RedTeamRun)
def get_redteam_run(
    run_id: str,
    db: Session = Depends(get_db),
) -> RedTeamRun:
    """Retrieve details and attack case results for a specific red-team run."""
    service = RedTeamService(db)
    run = service.get_run(run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Red-team run with ID '{run_id}' not found.",
        )
    return run
