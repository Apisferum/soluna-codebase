from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.db.database import (
    initialize_auth_tables,
    initialize_generation_tables,
)
from app.services.audio_runtime import start_audio_runtime, stop_audio_runtime


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncIterator[None]:
    settings.data_dir.mkdir(
        parents=True,
        exist_ok=True,
    )
    settings.generated_dir.mkdir(
        parents=True,
        exist_ok=True,
    )
    settings.separated_dir.mkdir(
        parents=True,
        exist_ok=True,
    )
    settings.composer_output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    initialize_auth_tables()
    initialize_generation_tables()

    await start_audio_runtime(app)

    yield

    await stop_audio_runtime(app)
