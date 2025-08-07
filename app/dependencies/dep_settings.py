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

def get_log_settings(
    log_level: str | None = None,
    log_redaction: bool | None = None,
    log_redaction_mode: str | None = None,
    log_sink_stdout: bool | None = None,
    log_sink_stderr: bool | None = None,
    log_sink_file: str | None = None,
    log_serialization: bool | None = None,
    log_enqueue: bool | None = None,
    log_diagnose: bool | None = None,
) -> LogSettings:
    """Returns log settings configuration from settings, with optional override.

    example:
    # Contoh override: level DEBUG dan sink file custom
        >>> log_settings = get_log_settings(
            ... log_level="DEBUG",
            ... log_sink_file="logs/custom.log"
        ... )
        >>> setup_loguru(
                level=log_settings.log_level,
                redaction=log_settings.log_redaction,
                redaction_mode=log_settings.log_redaction_mode,
                sink_stdout=log_settings.log_sink_stdout,
                sink_stderr=log_settings.log_sink_stderr,
        )
    # Jika ingin tetap auto profile (tanpa override), cukup:
        >>> log_settings = get_log_settings()
    """
    settings: Settings = get_settings()
    profile = settings.log_profile.copy()

    # Override profile with provided params if not None
    if log_level is not None:
        profile["log_level"] = log_level
    if log_redaction is not None:
        profile["log_redaction"] = log_redaction
    if log_redaction_mode is not None:
        profile["log_redaction_mode"] = log_redaction_mode
    if log_sink_stdout is not None:
        profile["log_sink_stdout"] = log_sink_stdout
    if log_sink_stderr is not None:
        profile["log_sink_stderr"] = log_sink_stderr
    if log_sink_file is not None:
        profile["log_sink_file"] = log_sink_file
    if log_serialization is not None:
        profile["log_serialization"] = log_serialization
    if log_enqueue is not None:
        profile["log_enqueue"] = log_enqueue
    if log_diagnose is not None:
        profile["log_diagnose"] = log_diagnose

    return LogSettings(**profile)

# FastAPI Dependencies
AppConfigDep = Annotated[AppConfig, Depends(get_app_config)]
SecurityConfigDep = Annotated[SecurityConfig, Depends(get_security_config)]
PathConfigDep = Annotated[PathConfig, Depends(get_path_config)]
LogSettingsDep = Annotated[LogSettings, Depends(get_log_settings)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
