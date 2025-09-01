from app.config.settings import Settings
from app.config.values import EnvironmentEnums
from loguru import logger


def test_test_settings_fixture(test_settings: Settings):
    """Ensure test_settings fixture returns correct values for testing."""
    # Adjusted to match nested config structure
    assert test_settings.ENV.environment == EnvironmentEnums.TESTING
    assert isinstance(test_settings.ENV.debug, bool)
    assert isinstance(test_settings.ENV.name, str)


def test_loguru_intercept(caplog):
    """Ensure loguru logs are intercepted and can be asserted via caplog."""
    logger.info("Hello from loguru!")
    assert "Hello from loguru!" in caplog.text
