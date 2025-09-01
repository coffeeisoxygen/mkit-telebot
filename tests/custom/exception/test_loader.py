# ruff: Noqa
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.custom.exception.base_exc import AppExceptionError
from app.custom.exception.loader import JSONResponse, register_exception_handlers


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
    assert response.json()["name"] == "RequestValidationError"
