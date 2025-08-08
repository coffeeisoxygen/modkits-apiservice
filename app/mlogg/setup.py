"""Main logging setup orchestrator."""

import functools
from collections.abc import Callable
from typing import Any

from app.mlogg.core import (
    ensure_log_directory,
    opener,
    setup_stdlib_integration,
    setup_stream_redirection,
)
from app.mlogg.environments import EnvironmentAwareSetup
from app.mlogg.security import SecurityConfig, sensitive_data_patcher
from loguru import logger


def setup_loguru(
    environment: str = "development",
    custom_config: dict[str, Any] | None = None,
    enable_stream_redirection: bool = True,
) -> None:
    """Setup loguru logger with environment-aware configuration.

    Args:
        environment: Environment name (development, testing, production)
        custom_config: Optional custom configuration to override defaults
        enable_stream_redirection: Whether to redirect stdout/stderr to loguru

    Example:
        >>> # Simple setup for development
        >>> setup_loguru("development")

        >>> # Production setup
        >>> setup_loguru("production")

        >>> # Custom configuration
        >>> setup_loguru("development", {"log_level": "INFO"})
    """
    logger.remove()  # Remove default logger

    # Initialize environment-aware setup
    env_setup = EnvironmentAwareSetup(environment)

    # Apply custom configuration if provided
    if custom_config:
        for key, value in custom_config.items():
            if hasattr(env_setup.config, key):
                setattr(env_setup.config, key, value)

        # Recreate security config with updated settings
        env_setup.security_config = SecurityConfig(
            enable_redaction=env_setup.config.enable_redaction,
            redaction_mode=env_setup.config.redaction_mode,
            environment=env_setup.environment,
        )

    # Setup security redaction if enabled (BEFORE adding sinks)
    if env_setup.security_config.should_redact:
        logger.configure(patcher=sensitive_data_patcher)
        redaction_mode = env_setup.security_config.effective_redaction_mode
        logger.info(f"🛡️ Sensitive data redaction enabled (mode: {redaction_mode})")

    # Add sinks based on environment configuration
    sink_configs = env_setup.get_sink_configs()
    for sink_config in sink_configs:
        # File sink - ensure directory exists and set opener
        if isinstance(sink_config["sink"], str):
            ensure_log_directory(sink_config["sink"])
            sink_config["opener"] = opener

        logger.add(**sink_config)

    # Setup integrations
    setup_stdlib_integration()

    # Optional stream redirection
    if enable_stream_redirection:
        setup_stream_redirection()

    logger.info(f"🚀 Logging initialized for environment: {environment}")


def get_environment_from_app_config(app_config: Any) -> str:
    """Extract environment from app configuration."""
    if hasattr(app_config, "env"):
        return str(app_config.env.value)
    elif hasattr(app_config, "environment"):
        return str(app_config.environment)
    else:
        return "development"  # fallback


def setup_from_settings(settings: Any, enable_stream_redirection: bool = True) -> None:
    """Setup logging from application settings.

    Args:
        settings: Application settings object with app configuration
        enable_stream_redirection: Whether to redirect stdout/stderr

    Example:
        >>> from app.config.settings import Settings
        >>> settings = Settings()
        >>> setup_from_settings(settings)
    """
    environment = get_environment_from_app_config(settings.app)
    setup_loguru(environment, enable_stream_redirection=enable_stream_redirection)


# Decorators for endpoint logging
def logtrace_endpoint(endpoint_name: str | None = None) -> Callable:
    """Decorator to log the start and end of an endpoint function.

    Args:
        endpoint_name: Optional custom name for the endpoint

    Example:
        >>> @logtrace_endpoint()
        >>> async def my_endpoint():
        >>>     return {"message": "Hello"}

        >>> @logtrace_endpoint("custom_name")
        >>> async def another_endpoint():
        >>>     return {"data": "value"}
    """

    def decorator(func: Callable) -> Callable:
        name = endpoint_name or func.__name__

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger.info(f"🎯 Executing endpoint: '{name}'")
            try:
                result = await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"❌ Error in endpoint '{name}': {e}")
                raise
            else:
                logger.info(f"✅ Finished endpoint: '{name}'")
                return result

        return wrapper

    return decorator


# Alias for backward compatibility
endpoint_logger = logtrace_endpoint
