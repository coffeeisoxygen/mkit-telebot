"""nested model for settings."""

from enum import StrEnum

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

from app._version import __version__ as app_version


class EnvironmentEnums(StrEnum):
    """enum for environment."""

    PRODUCTION = "PRODUCTION"
    DEVELOPMENT = "DEVELOPMENT"
    TESTING = "TESTING"


class ConfigEnvironment(BaseSettings):
    """core config for environment."""

    environment: EnvironmentEnums = EnvironmentEnums.PRODUCTION
    name: str = "MKIT-TELEBOT"
    version: str = app_version
    debug: bool = False

    @field_validator("environment", mode="before")
    @classmethod
    def normalize_env(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.upper()
        return v


class ConfigDatabase(BaseSettings):
    """Konfigurasi database untuk aplikasi."""

    url: str = "sqlite+aiosqlite:///./telebot.db"
    echo: bool = Field(
        default=False, description="Aktifkan logging SQL. Nonaktifkan untuk produksi."
    )

    timeout: int = Field(
        default=5, description="Waktu tunggu (detik) untuk koneksi database."
    )

    pool_size: int = Field(
        default=5, description="Jumlah koneksi yang disimpan dalam pool."
    )
    max_overflow: int = Field(
        default=10,
        description="Jumlah koneksi tambahan yang diizinkan saat pool penuh.",
    )
