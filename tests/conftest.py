from pathlib import Path

import pytest
from app.config import get_settings
from app.custom.mlogging.setup import setup_logging
from app.database import create_tables, sessionmanager
from app.exception import register_exception_handlers
from fastapi import FastAPI
from loguru import logger


@pytest.fixture(scope="function", autouse=True)
def test_settings():
    """
    Test settings fixture for the testing environment.

    This fixture provides the application settings for the testing environment.

    Returns:
        _type_: The application settings for the testing environment.
    """
    get_settings.cache_clear()
    test_env = Path(__file__).parent.parent / ".env.test"
    settings = get_settings(test_env)
    print(f" running on env {settings.ENV.environment}")  # noqa: T201
    return settings


@pytest.fixture(autouse=True)
def intercept_loguru(caplog: pytest.LogCaptureFixture):
    """
    Use the main loguru config for tests, and add a temporary loguru handler for caplog so loguru logs are captured by pytest.
    """
    config_path = Path(__file__).parent.parent / "config_log.yaml"
    setup_logging(config_path=config_path, env="test")

    handler_id = logger.add(
        sink=caplog.handler,
        level="DEBUG",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        enqueue=False,
    )
    yield
    logger.remove(handler_id)


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Create all tables before running tests."""
    await create_tables(sessionmanager.engine)


@pytest.fixture(scope="function")
async def db_session():
    """Yield an async database session for tests."""
    async with sessionmanager.session() as session:
        yield session


@pytest.fixture
def app_with_exception():
    app = FastAPI()
    register_exception_handlers(app)
    return app
