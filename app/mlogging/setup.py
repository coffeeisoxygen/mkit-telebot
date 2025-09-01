import inspect
import logging
from pathlib import Path

from loguru import logger
from loguru_config import LoguruConfig

from app.custom.mlogging.default import load_logging_config
from app.custom.mlogging.patcher import extra_patcher, masking_patcher


class InterceptHandler(logging.Handler):
    """Handler to intercept standard logging and forward to loguru.

    Use this to unify stdlib logging and loguru output.
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def patcher_wrapper(
    record: logging.LogRecord,
    masking_config: dict | None = None,
) -> None:
    """Wrapper agar semua patcher config bisa diakses oleh patcher."""
    if masking_config is not None:
        masking_patcher(record, masking_config)


def setup_logging(
    config_path: str | Path | None = None, env: str = "development"
) -> None:
    """Setup logging: intercept stdlib, propagate loggers, masking, exception, traceback, and loguru config.

    Args:
        config_path: Path to YAML config file (optional).
        env: Environment name (default: "development").
    """
    config = load_logging_config(config_path)

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    if config.propogate.enabled:
        for logger_name in config.propogate.loggers_name:
            logging_logger = logging.getLogger(logger_name)
            logging_logger.handlers = []
            logging_logger.propagate = True
            if config.propogate.level_to_pass:
                logging_logger.setLevel(config.propogate.level_to_pass)

    # Tentukan sumber log
    source = "default"
    if config_path is not None:
        source = (
            Path(config_path).name
            if isinstance(config_path, (str, Path))
            else str(config_path)
        )

    # Convert config to dict for LoguruConfig
    config_dict = config.model_dump(exclude={"masking", "propogate"})
    LoguruConfig.load(config_or_file=config_dict, configure=True)

    default_extra = {"env": env, "source": source}

    def patcher(record):
        patcher_wrapper(record, masking_config=config.masking.model_dump())
        extra_patcher(record, default_extra)

    LoguruConfig(
        extra=default_extra,
        patcher=patcher,
    ).configure()
