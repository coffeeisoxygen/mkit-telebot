# ruff: Noqa
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exception import AppExceptionError


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
        # Mengambil errors dari Pydantic
        errors = jsonable_encoder(exc.errors())

        # Membuat pesan error yang diseragamkan
        # Anda bisa menyederhanakan format di sini sesuai kebutuhan
        error_message = "Validation failed for the request body."

        return JSONResponse(
            status_code=422,
            content={
                "name": "ValidationError",
                "message": error_message,
                "status_code": 422,
                "context": {"errors": errors},
                "cause": None,
            },
        )
