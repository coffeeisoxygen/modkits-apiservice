"""module for applications core settings."""

from app.config.cfg_app import AppConfig
from app.config.cfg_jwt import JwtConfig, TokenConfig
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    # App Global Information and setup
    appinfo: AppConfig

    # Jwt Setup
    jwt_config: JwtConfig
    token_config: TokenConfig

    @property
    def is_dev(self) -> bool:
        return self.appinfo.is_development

    @property
    def is_prod(self) -> bool:
        return self.appinfo.is_production

    @property
    def is_test(self) -> bool:
        return self.appinfo.is_testing
