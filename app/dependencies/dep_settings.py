"""agar tidak muter muter import dan dependensi.

agar tidak ribet klo import dan pas butuh, jadi di buat lah dependencies settings ini.
"""

import os
from functools import lru_cache
from typing import Annotated

from app.core.settings import (
    AppConfig,
    LogSettings,
    PathConfig,
    SecurityConfig,
    Settings,
)
from fastapi import Depends


@lru_cache
def get_settings() -> Settings:
    """Dynamic environment loading using _env_file parameter."""
    app_env = os.getenv("APP_ENV", "development").lower()
    env_files = [".env"]  # Base file always loaded first

    if app_env == "production":
        env_files.append(".env.prod")
    elif app_env == "testing":
        env_files.append(".env.test")
    else:  # development (default)
        env_files.append(".env.dev")

    # Using Pydantic Settings _env_file parameter for runtime loading
    return Settings(_env_file=env_files)  # type: ignore


def get_app_config() -> AppConfig:
    """Returns app configuration from settings."""
    settings: Settings = get_settings()
    return settings.app


def get_security_config() -> SecurityConfig:
    """Returns security configuration from settings."""
    settings: Settings = get_settings()
    return settings.security


def get_path_config() -> PathConfig:
    """Returns path configuration from settings."""
    settings: Settings = get_settings()
    return settings.data_paths

def get_log_settings() -> LogSettings:
    """Returns log settings configuration from settings."""
    settings: Settings = get_settings()
    return LogSettings(
        log_level=settings.log_level,
        log_redaction=settings.log_redaction,
        log_redaction_mode=settings.log_redaction_mode,
        log_sink_stdout=settings.log_sink_stdout,
        log_sink_stderr=settings.log_sink_stderr,
    )

# FastAPI Dependencies
AppConfigDep = Annotated[AppConfig, Depends(get_app_config)]
SecurityConfigDep = Annotated[SecurityConfig, Depends(get_security_config)]
PathConfigDep = Annotated[PathConfig, Depends(get_path_config)]
LogSettingsDep = Annotated[LogSettings, Depends(get_log_settings)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
