from app.core.settings import AppConfig, PathConfig, SecurityConfig, Settings
from app.dependencies.dep_settings import (
    get_app_config,
    get_path_config,
    get_security_config,
    get_settings,
)


def test_get_settings_env(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    settings = get_settings()
    assert isinstance(settings, Settings)
    assert settings.app_env in ["production", "development", "testing"]


def test_get_app_config_returns_appconfig():
    app_config = get_app_config()
    assert isinstance(app_config, AppConfig)


def test_get_security_config_returns_securityconfig():
    sec_config = get_security_config()
    assert isinstance(sec_config, SecurityConfig)


def test_get_path_config_returns_pathconfig():
    path_config = get_path_config()
    assert isinstance(path_config, PathConfig)


def test_get_settings_env_file(monkeypatch):
    monkeypatch.setenv("APP_ENV", "testing")
    settings = get_settings()
    assert settings.app_env == "testing" or settings.app_env == "development"
