"""module for applications core settings.

beberapa settings models di comments karena tidak relate untuk env saat ini
untuk menghindati complexity, hanya yang digunakan saat ini yang diaktifkan
untuk yang lain bisa diaktifkan jika diperlukan.
"""

from app.config.cfg_app import AppConfig
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    """Application settings with nested configuration.

    >>> Multiple environment files - loading order matters!
    >>> Files loaded in order: .env -> .env.dev/.env.prod (based on APP_ENV)
    >>> Will be overridden by _env_file based on environment

    """

    model_config = SettingsConfigDict(
        env_file=(
            ".env",
            ".env.dev",
        ),
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="allow",
    )

    appinfo: AppConfig

    # Security Settings
    security_secret_key: str = Field(
        default="default-secret-key", alias="SECURITY_SECRET_KEY"
    )
    security_algorithm: str = Field(default="HS256", alias="SECURITY_ALGORITHM")
    token_expiration_minutes: int = Field(default=60, alias="TOKEN_EXPIRATION_MINUTES")

    # Log Settings
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_redaction: bool = Field(default=True, alias="LOG_REDACTION")
    log_redaction_mode: str = Field(default="hash", alias="LOG_REDACTION_MODE")
    log_sink_stdout: bool = Field(default=True, alias="LOG_SINK_STDOUT")
    log_sink_stderr: bool = Field(default=True, alias="LOG_SINK_STDERR")
    log_sink_file: str | None = Field(default=None, alias="LOG_SINK_FILE")
    log_serialization: bool = Field(default=True, alias="LOG_SERIALIZATION")
    log_enqueue: bool = Field(default=True, alias="LOG_ENQUEUE")
    log_diagnose: bool = Field(default=True, alias="LOG_DIAGNOSE")
    log_format: str | None = Field(default=None, alias="LOG_FORMAT")

    # @property
    # def security(self) -> SecurityConfig:
    #     """Get security configuration."""
    #     return SecurityConfig(
    #         secret_key=self.security_secret_key, algorithm=self.security_algorithm
    #     )

    # @property
    # def token(self) -> TokenConfig:
    #     """Get token configuration."""
    #     return TokenConfig(token_expiration_minutes=self.token_expiration_minutes)

    # @property
    # def data_paths(self) -> PathConfig:
    #     """Get paths configuration."""
    #     return PathConfig(data=self.path_data, keys=self.path_keys)

    # @property
    # def is_production(self) -> bool:
    #     """Check if running in production."""
    #     return self.app_env == EnvironmentEnum.PRODUCTION

    # @property
    # def is_development(self) -> bool:
    #     """Check if running in development."""
    #     return self.app_env == EnvironmentEnum.DEVELOPMENT

    # @property
    # def debug(self) -> bool:
    #     """Get debug flag."""
    #     return self.app_debug

    # @property
    # def environment(self) -> EnvironmentEnum:
    #     """Get environment."""
    #     return self.app_env

    # @property
    # def service(self) -> str:
    #     """Get service name."""
    #     return self.app_service

    # @property
    # def version(self) -> str:
    #     """Get version."""
    #     return self.app_version

    # @property
    # def log_profile(self):
    #     """Logging profile setup based on environment.

    #     habit logging pada prod dan dev sangat berbeda
    #     dengan ada nya profile , auto switch nya akan sangat nyaman sekali
    #     """
    #     if self.is_production:
    #         return {
    #             "log_level": "INFO",
    #             "log_redaction": True,
    #             "log_redaction_mode": "hash",
    #             "log_sink_stdout": False,
    #             "log_sink_stderr": True,
    #             "log_sink_file": "logs/app.log",
    #             "log_serialization": True,
    #             "log_enqueue": True,
    #             "log_diagnose": False,
    #             "log_format": "",
    #         }
    #     # Default development settings
    #     return {
    #         "log_level": "DEBUG",
    #         "log_redaction": True,
    #         "log_redaction_mode": "hash",
    #         "log_sink_stdout": True,
    #         "log_sink_stderr": True,
    #         "log_sink_file": None,
    #         "log_serialization": True,
    #         "log_enqueue": True,
    #         "log_diagnose": True,
    #         "log_format": "",
    #     }
