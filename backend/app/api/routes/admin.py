from fastapi import APIRouter, Depends

from app.core.security import (
    public_user,
    require_admin,
)
from app.schemas.auth import ProfileResponse


router = APIRouter()


@router.get(
    "/me",
    response_model=ProfileResponse,
)
def get_admin_profile(
    current_admin=Depends(require_admin),
) -> ProfileResponse:
    return ProfileResponse(
        user=public_user(current_admin)
    )

@router.get("/research/runs")
def get_research_runs(
    current_admin=Depends(require_admin),
):
    del current_admin
    return {"runs": []}


@router.get("/research/dashboard")
def get_research_dashboard(
    run_id: int | None = None,
    batch_limit: int = 5000,
    current_admin=Depends(require_admin),
):
    del current_admin, run_id, batch_limit
    return {
        "run": None,
        "summary": None,
        "epochs": [],
        "tasks": [],
        "taskSeries": {},
        "batches": [],
    }
