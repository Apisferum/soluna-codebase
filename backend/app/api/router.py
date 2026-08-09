from fastapi import APIRouter

from app.api.routes import (
    admin,
    audio_analysis,
    audio_separation,
    auth,
    composer,
    generations,
    health,
    users,
    websocket,
)

api_router = APIRouter()

api_router.include_router(
    health.router,
    tags=["System"],
)

api_router.include_router(
    audio_analysis.router,
    tags=["Chord AI"],
)

api_router.include_router(
    audio_separation.router,
    tags=["Stem Separator"],
)

api_router.include_router(
    websocket.router,
    tags=["Chord AI"],
)

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
)

api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["Administration"],
)

api_router.include_router(
    generations.router,
    tags=["Generations"],
)

api_router.include_router(
    composer.router,
    prefix="/composer",
    tags=["Composer"],
)
