from app.config.settings import Settings
from app.config.values import EnvironmentEnums


def test_test_settings_fixture(test_settings: Settings):
    """Ensure test_settings fixture returns correct values for testing."""
    # Adjusted to match nested config structure
    assert test_settings.ENV.environment == EnvironmentEnums.TESTING
    assert isinstance(test_settings.ENV.debug, bool)
    assert isinstance(test_settings.ENV.name, str)
