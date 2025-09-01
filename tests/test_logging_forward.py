import importlib
import logging

from loguru import logger

# Import the InterceptHandler setup
importlib.import_module("app.custom.mlogging.setup")


def test_standard_logging_forwarded_to_loguru(caplog):
    """Test that standard logging messages are forwarded to loguru and captured by caplog."""
    logging.getLogger().info("Standard logging info message")
    logger.info("Direct loguru info message")
    assert "Standard logging info message" in caplog.text
    assert "Direct loguru info message" in caplog.text
