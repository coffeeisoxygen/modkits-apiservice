"""module for applications core settings.

beberapa settings models di comments karena tidak relate untuk env saat ini
untuk menghindati complexity, hanya yang digunakan saat ini yang diaktifkan
untuk yang lain bisa diaktifkan jika diperlukan.
"""

from enum import StrEnum

from app._version import __version__ as version
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentEnum(StrEnum):
    """Environment types."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class AppConfig(BaseModel):
    """Application configuration."""

    debug: bool
    env: EnvironmentEnum
    service: str
    version: str


class SecurityConfig(BaseModel):
    """Security and encryption configuration."""

    secret_key: str
    algorithm: str


class TokenConfig(BaseModel):
    """Token configuration."""

    token_expiration_minutes: int


class PathConfig(BaseModel):
    """File paths configuration."""

    data: str
    keys: str


class Settings(BaseSettings):
    """Application settings with nested configuration."""

    model_config = SettingsConfigDict(
        # Multiple environment files - loading order matters!
        # Files loaded in order: .env -> .env.dev/.env.prod (based on APP_ENV)
        env_file=(
            ".env",
            ".env.dev",
        ),  # Will be overridden by _env_file based on environment
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    # Application Settings
    app_debug: bool = Field(default=False, alias="APP_DEBUG")
    app_env: EnvironmentEnum = Field(
        default=EnvironmentEnum.DEVELOPMENT, alias="APP_ENV"
    )
    app_service: str = Field(default="mod-apiparser", alias="APP_SERVICE")
    app_version: str = Field(default=version, alias="APP_VERSION")

    # Security Settings
    security_secret_key: str = Field(
        default="default-secret-key", alias="SECURITY_SECRET_KEY"
    )
    security_algorithm: str = Field(default="HS256", alias="SECURITY_ALGORITHM")
    token_expiration_minutes: int = Field(default=60, alias="TOKEN_EXPIRATION_MINUTES")

    path_data: str = Field(default="secrets/data", alias="PATH_DATA")
    path_keys: str = Field(default="secrets/keys", alias="PATH_KEYS")

    @property
    def app(self) -> AppConfig:
        """Get app configuration."""
        return AppConfig(
            debug=self.app_debug,
            env=self.app_env,
            service=self.app_service,
            version=self.app_version,
        )

    @property
    def security(self) -> SecurityConfig:
        """Get security configuration."""
        return SecurityConfig(
            secret_key=self.security_secret_key, algorithm=self.security_algorithm
        )

    @property
    def token(self) -> TokenConfig:
        """Get token configuration."""
        return TokenConfig(token_expiration_minutes=self.token_expiration_minutes)

    @property
    def data_paths(self) -> PathConfig:
        """Get paths configuration."""
        return PathConfig(data=self.path_data, keys=self.path_keys)

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.app_env == EnvironmentEnum.PRODUCTION

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.app_env == EnvironmentEnum.DEVELOPMENT

    @property
    def debug(self) -> bool:
        """Get debug flag."""
        return self.app_debug

    @property
    def environment(self) -> EnvironmentEnum:
        """Get environment."""
        return self.app_env

    @property
    def service(self) -> str:
        """Get service name."""
        return self.app_service

    @property
    def version(self) -> str:
        """Get version."""
        return self.app_version
