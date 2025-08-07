from app.core.settings import (
    AppConfig,
    EnvironmentEnum,
    PathConfig,
    SecurityConfig,
    Settings,
    TokenConfig,
)


def test_settings_defaults():
    settings = Settings()
    assert isinstance(settings, Settings)
    assert settings.app_debug is False
    assert settings.app_env == EnvironmentEnum.DEVELOPMENT
    assert settings.app_service == "mod-apiparser"
    assert isinstance(settings.app, AppConfig)
    assert isinstance(settings.security, SecurityConfig)
    assert isinstance(settings.token, TokenConfig)
    assert isinstance(settings.data_paths, PathConfig)


def test_app_property():
    settings = Settings(
        app_debug=True,
        app_env=EnvironmentEnum.TESTING,
        app_service="test-service",
        app_version="1.2.3",
    )
    app = settings.app
    assert app.debug is True
    assert app.env == EnvironmentEnum.TESTING
    assert app.service == "test-service"
    assert app.version == "1.2.3"


def test_security_property():
    settings = Settings(security_secret_key="abc", security_algorithm="RS256")
    sec = settings.security
    assert sec.secret_key == "abc"
    assert sec.algorithm == "RS256"


def test_token_property():
    settings = Settings(token_expiration_minutes=123)
    token = settings.token
    assert token.token_expiration_minutes == 123


def test_data_paths_property():
    settings = Settings(path_data="foo", path_keys="bar")
    paths = settings.data_paths
    assert paths.data == "foo"
    assert paths.keys == "bar"


def test_is_production_and_is_development():
    settings_prod = Settings(app_env=EnvironmentEnum.PRODUCTION)
    settings_dev = Settings(app_env=EnvironmentEnum.DEVELOPMENT)
    assert settings_prod.is_production is True
    assert settings_prod.is_development is False
    assert settings_dev.is_development is True
    assert settings_dev.is_production is False


def test_debug_and_environment_properties():
    settings = Settings(app_debug=True, app_env=EnvironmentEnum.TESTING)
    assert settings.debug is True
    assert settings.environment == EnvironmentEnum.TESTING


def test_service_and_version_properties():
    settings = Settings(app_service="svc", app_version="v1")
    assert settings.service == "svc"
    assert settings.version == "v1"
