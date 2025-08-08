"""Dependency injection untuk settings application.

Modul ini menyediakan akses ke konfigurasi aplikasi melalui dependency injection,
mengikuti prinsip loose coupling dan separation of concerns.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from app.config.settings import (
    AppConfig,
    JwtConfig,
    Settings,
)
from fastapi import Depends


@lru_cache
def get_settings() -> Settings:
    """Get application settings dengan environment-specific configuration.

    Fungsi ini memuat settings dari file environment berdasarkan nilai APP_ENV.
    Menggunakan LRU cache untuk memastikan settings hanya dimuat sekali selama
    lifecycle aplikasi.

    File environment dimuat dengan urutan:
    1. Base .env file (selalu)
    2. File spesifik environment (.env.dev, .env.prod, .env.test)

    Returns:
        Settings: Objek settings aplikasi yang terkonfigurasi
    """
    app_env = os.getenv("APP_ENV", "development").lower()
    env_files = [".env"]  # Base file always loaded first

    if app_env == "production":
        env_files.append(".env.prod")
    elif app_env == "testing":
        env_files.append(".env.test")
    else:  # development (default)
        env_files.append(".env.dev")

    # Verify files exist
    for env_file in env_files:
        if not os.path.isfile(env_file):
            import warnings

            warnings.warn(f"Environment file {env_file} tidak ditemukan")

    # Pass absolute paths to ensure files are found
    abs_paths = [os.path.abspath(path) for path in env_files]
    return Settings(_env_file=abs_paths)  # type: ignore


def get_app_config() -> AppConfig:
    """Get app configuration dari settings.

    Dependency ini memungkinkan injeksi hanya bagian AppConfig
    dari settings, mengikuti prinsip minimal dependencies.

    Returns:
        AppConfig: Konfigurasi aplikasi
    """
    settings = get_settings()
    return settings.app


def get_jwt_config() -> JwtConfig:
    """Get JWT security configuration dari settings.

    Returns:
        JwtConfig: Pengaturan konfigurasi JWT
    """
    settings = get_settings()
    return settings.jwt


def get_path_settings() -> tuple[Path, Path]:
    """Get path settings dari application config.

    Dependency ini memungkinkan akses langsung ke path settings
    tanpa perlu mengakses seluruh AppConfig, mengikuti prinsip
    minimal dependencies.

    Returns:
        Tuple[Path, Path]: Tuple berisi (path_data, path_keys)
    """
    app_config = get_app_config()
    return app_config.path_data, app_config.path_keys


# FastAPI Dependencies (type-safe)
SettingsDep = Annotated[Settings, Depends(get_settings)]
AppConfigDep = Annotated[AppConfig, Depends(get_app_config)]
JwtConfigDep = Annotated[JwtConfig, Depends(get_jwt_config)]
PathSettingsDep = Annotated[tuple[Path, Path], Depends(get_path_settings)]
