# ruff: Noqa
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.custom.exception.base_exc import AppExceptionError


def register_exception_handlers(app) -> None:  # noqa: ANN001
    """Register all custom exception handlers to FastAPI app.

    Args:
        app (FastAPI): The FastAPI application instance.
    """

    @app.exception_handler(AppExceptionError)
    def app_exception_handler(_, exc: AppExceptionError):  # noqa: ANN001
        return JSONResponse(
            status_code=exc.status_code or 500,
            content=exc.to_dict(),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "name": "HTTPError",
                "message": exc.detail,
                "status_code": exc.status_code,
                "context": {},
                "cause": None,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        return JSONResponse(
            status_code=422,
            content={
                "name": "RequestValidationError",
                "message": str(exc),
                "errors": exc.errors() if hasattr(exc, "errors") else None,
            },
        )
