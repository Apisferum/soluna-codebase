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