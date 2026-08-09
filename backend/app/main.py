import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.lifespan import lifespan
from app.core.middleware import register_middleware

ROOT_DIR = Path(__file__).resolve().parents[2]
DIST_DIR = ROOT_DIR / "dist"


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    register_middleware(application)
    register_exception_handlers(application)

    application.include_router(
        api_router,
        prefix=settings.api_prefix,
    )

    assets_dir = DIST_DIR / "assets"
    if assets_dir.exists():
        application.mount("/assets", StaticFiles(directory=str(assets_dir)), name="frontend-assets")

    @application.get("/", include_in_schema=False)
    async def serve_index() -> FileResponse:
        index_path = DIST_DIR / "index.html"
        if not index_path.exists():
            raise HTTPException(status_code=404, detail="Frontend build not found")
        return FileResponse(index_path)

    @application.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str) -> FileResponse:
        if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("openapi"):
            raise HTTPException(status_code=404, detail="Not found")

        candidate = (DIST_DIR / full_path).resolve()
        if candidate.exists() and candidate.is_file():
            return FileResponse(candidate)

        index_path = DIST_DIR / "index.html"
        if not index_path.exists():
            raise HTTPException(status_code=404, detail="Frontend build not found")
        return FileResponse(index_path)

    return application


app = create_application()
