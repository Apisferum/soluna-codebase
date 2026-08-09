from fastapi import APIRouter, Depends

from app.core.security import (
    get_current_user,
    public_user,
)
from app.schemas.auth import ProfileResponse


router = APIRouter()


@router.get(
    "/me",
    response_model=ProfileResponse,
)
def get_my_profile(
    current_user=Depends(get_current_user),
) -> ProfileResponse:
    return ProfileResponse(
        user=public_user(current_user)
    )