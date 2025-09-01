from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


def load_logging_config(config_path: str | Path | None = None) -> "LoggingConfig":
    """Load LoggingConfig from YAML file, fallback to default if not found or error."""
    if config_path is not None:
        try:
            with open(config_path, encoding="utf-8") as file:
                config_dict = yaml.safe_load(file)
            # Pydantic will handle nested dicts automatically
            return LoggingConfig(**config_dict)
        except Exception:
            pass
    return LoggingConfig()


class MaskingConfig(BaseModel):
    enabled: bool = True
    mask_message: bool = True
    mask_extra: bool = True
    default_mask: str = "XXXXXXXX"
    mask_regex: dict[str, str] = Field(
        default_factory=lambda: {
            "credit_card": "\\b\\d{4}[\\s-]?\\d{4}[\\s-]?\\d{4}[\\s-]?\\d{4}\\b",
            "email": "\\b[\\w.-]+@[\\w.-]+\\.\\w+\\b",
            "password": "(?i)password\\s*:\\s*\\S+",
            "token": "(?i)token\\s*:\\s*\\S+",
        }
    )
    mask_fields: list[str] = Field(
        default_factory=lambda: ["password", "token", "secret", "card"]
    )


class PropogateConfig(BaseModel):
    enabled: bool = True
    level_to_pass: str = "INFO"
    loggers_name: list[str] = Field(
        default_factory=lambda: [
            "uvicorn",
            "uvicorn.access",
            "uvicorn.error",
            "fastapi",
            "asyncio",
            "starlette",
        ]
    )


class HandlerConfig(BaseModel):
    sink: str = "ext://sys.stdout"
    level: str = "DEBUG"
    format: str = "<level>{level: <8}</level>| <magenta>{name}</magenta>:<bold>{function}</bold>:<magenta>{line}</magenta> | <level>{message}</level> | <l>{extra}</>"
    enqueue: bool = True
    diagnose: bool = True
    backtrace: bool = True


class LoggingConfig(BaseModel):
    masking: MaskingConfig = MaskingConfig()
    propogate: PropogateConfig = PropogateConfig()
    handlers: list[HandlerConfig] = Field(default_factory=lambda: [HandlerConfig()])
    extra: dict[str, Any] = Field(default_factory=lambda: {"env": "override me please"})
    activation: list[list[Any]] = Field(
        default_factory=lambda: [
            ["uvicorn.watchfiles", False],
            ["uvicorn.protocols", False],
            ["watchfiles", False],
            ["another_library.module", True],
        ]
    )
