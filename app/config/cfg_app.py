"""module ini untuk define setting setting."""

from enum import StrEnum
from pathlib import Path

from app._version import __version__ as version
from pydantic import BaseModel, Field, field_validator


class EnvironmentEnum(StrEnum):
    """Environment types."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class AppConfig(BaseModel):
    """Application configuration."""

    debug: bool = Field(default=False, alias="APP_DEBUG")
    env: EnvironmentEnum = Field(default=EnvironmentEnum.DEVELOPMENT, alias="APP_ENV")
    service: str = Field(default="MODKIT-APISERVICES", alias="APP_SERVICE")
    version: str = Field(default=version, alias="APP_VERSION")
    path_data: Path = Field(default=Path("secrets/data"), alias="APP_PATH_DATA")
    path_keys: Path = Field(default=Path("secrets/keys"), alias="APP_PATH_KEYS")
    create_missing_paths: bool = Field(default=True, alias="APP__CREATE_MISSING_PATHS")

    @field_validator("env", mode="before")
    @classmethod
    def validate_env(cls, v: str | EnvironmentEnum) -> EnvironmentEnum:
        """Validasi string env ke EnvironmentEnum."""
        if isinstance(v, EnvironmentEnum):
            return v
        try:
            return EnvironmentEnum(v.strip().lower())
        except ValueError:
            raise ValueError(
                f"env harus salah satu dari: {[e.value for e in EnvironmentEnum]}"
            ) from None

    @field_validator("path_data", "path_keys", mode="after")
    @classmethod
    def validate_path_exists(cls, path: Path, info) -> Path:  # noqa: ANN001
        """Validasi path sudah ada, atau buat jika belum ada."""
        # Get create_missing_paths from validation context or use default
        model_data = info.data
        create_missing = model_data.get("create_missing_paths", True)

        # Ensure path is absolute
        if not path.is_absolute():
            path = Path.cwd() / path

        # Check if path exists, create if necessary
        if not path.exists():
            if create_missing:
                try:
                    path.mkdir(parents=True, exist_ok=True)
                except PermissionError as e:
                    raise ValueError(
                        f"Tidak bisa membuat direktori: {path} (permission denied)"
                    ) from e
                except OSError as e:
                    raise ValueError(
                        f"Error saat membuat direktori {path}: {e!s}"
                    ) from e
            else:
                raise ValueError(f"Path tidak ditemukan: {path}")

        # Ensure it's a directory
        if not path.is_dir():
            raise ValueError(f"Path bukan direktori: {path}")

        return path

    @property
    def is_development(self) -> bool:
        """Check if environment is development."""
        return self.env == EnvironmentEnum.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        """Check if environment is production."""
        return self.env == EnvironmentEnum.PRODUCTION

    @property
    def is_testing(self) -> bool:
        """Check if environment is testing."""
        return self.env == EnvironmentEnum.TESTING

    @property
    def log_level(self) -> str:
        """Get appropriate log level based on environment."""
        if self.is_development:
            return "DEBUG"
        elif self.is_testing:
            return "INFO"
        else:
            return "WARNING"  # Production default
