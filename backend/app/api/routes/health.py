from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import HealthResponse, RootResponse


router = APIRouter()


@router.get(
    "/",
    response_model=RootResponse,
    summary="Backend information",
)
async def root() -> RootResponse:
    return RootResponse(
        message="Synestra unified backend is running",
        service=settings.app_name,
        version=settings.app_version,
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.app_name,
    )
