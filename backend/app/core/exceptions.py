import logging

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


logger = logging.getLogger("synestra.errors")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        # Keep FastAPI's normal validation-error structure
        # so existing frontend and Postman tests continue working.
        return JSONResponse(
            status_code=422,
            content={
                "detail": jsonable_encoder(exc.errors()),
            },
        )

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        request_id = getattr(
            request.state,
            "request_id",
            None,
        )

        logger.exception(
            "Unexpected application error: path=%s request_id=%s",
            request.url.path,
            request_id,
        )

        content = {
            "detail": "An unexpected server error occurred",
        }

        if request_id:
            content["request_id"] = request_id

        return JSONResponse(
            status_code=500,
            content=content,
        )
