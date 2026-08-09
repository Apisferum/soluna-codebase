import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


logger = logging.getLogger("synestra.requests")


def register_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_logging_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get(
            "X-Request-ID",
            str(uuid.uuid4()),
        )

        request.state.request_id = request_id
        started_at = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (
                time.perf_counter() - started_at
            ) * 1000

            logger.exception(
                (
                    "Unhandled request error: "
                    "method=%s path=%s duration_ms=%.2f "
                    "request_id=%s"
                ),
                request.method,
                request.url.path,
                duration_ms,
                request_id,
            )
            raise

        duration_ms = (
            time.perf_counter() - started_at
        ) * 1000

        response.headers["X-Request-ID"] = request_id

        logger.info(
            (
                "method=%s path=%s status=%s "
                "duration_ms=%.2f request_id=%s"
            ),
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            request_id,
        )

        return response
