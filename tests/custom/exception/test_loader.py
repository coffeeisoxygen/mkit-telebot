# ruff: Noqa
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
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


app = FastAPI()
register_exception_handlers(app)


@app.get("/raise-app-exc")
def raise_app_exc():
    raise AppExceptionError(message="Test error")


@app.get("/raise-validation")
def raise_validation(item: int):
    return {"item": item}


client = TestClient(app)


def test_app_exception_handler():
    response = client.get("/raise-app-exc")
    assert response.status_code == 500
    assert response.json()["message"] == "Test error"


def test_validation_exception_handler():
    response = client.get("/raise-validation?item=abc")
    assert response.status_code == 422
    assert response.json()["name"] == "ValidationError"
