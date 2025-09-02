import logging
from pathlib import Path

import pytest
import asyncio
from app.config import get_settings
from app.custom.mlogging.setup import setup_logging
from app.database import DatabaseSessionManager, create_tables, sessionmanager
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

    # Override sessionmanager to use test DB
    sessionmanager.engine = DatabaseSessionManager(settings.DB.url).engine
    sessionmanager._sessionmaker = DatabaseSessionManager(settings.DB.url)._sessionmaker
    # Langsung create tables setelah override DB
    asyncio.get_event_loop().run_until_complete(create_tables(sessionmanager.engine))
    return settings


@pytest.fixture(autouse=True)
def intercept_loguru(caplog: pytest.LogCaptureFixture):
    """
    Use the main loguru config for tests, and add a temporary loguru handler for caplog so loguru logs are captured by pytest.
    """
    config_path = Path(__file__).parent.parent / "config_log.yaml"
    setup_logging(config_path=config_path, env="test")

    # Silence noisy libraries
    for noisy_logger in ["aiosqlite", "asyncio"]:
        logging.getLogger(noisy_logger).setLevel(logging.INFO)

    handler_id = logger.add(
        sink=caplog.handler,
        level="DEBUG",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        enqueue=False,
    )
    yield
    logger.remove(handler_id)


@pytest.fixture
def restore_sessionmanager():
    """
    Restore sessionmanager.engine and _sessionmaker after patching in tests.
    """
    orig_engine = sessionmanager.engine
    orig_sessionmaker = sessionmanager._sessionmaker
    yield
    sessionmanager.engine = orig_engine
    sessionmanager._sessionmaker = orig_sessionmaker


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Create all tables before running tests."""
    await create_tables(sessionmanager.engine)


@pytest.fixture(scope="function")
async def db_session():
    """Yield an async database session for tests."""
    async with sessionmanager.session() as session:
        yield session
