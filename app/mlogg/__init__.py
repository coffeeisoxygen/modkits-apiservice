"""Modern, environment-aware logging setup for FastAPI applications.

This module provides a clean, organized approach to logging with:
- Environment-specific configurations (development, testing, production)
- Sensitive data redaction with configurable modes
- Structured logging with appropriate formats per environment
- Integration with FastAPI, Uvicorn, and standard library logging

Example usage:
    # Simple setup
    >>> from app.mlogg import setup_loguru
    >>> setup_loguru("development")

    # Setup from app settings
    >>> from app.mlogg import setup_from_settings
    >>> setup_from_settings(settings)

    # Endpoint tracing
    >>> from app.mlogg import logtrace_endpoint
    >>> @logtrace_endpoint()
    >>> async def my_endpoint():
    >>>     return {"message": "Hello"}
"""

from app.mlogg.setup import (
    endpoint_logger,
    logtrace_endpoint,
    setup_from_settings,
    setup_loguru,
)

__all__ = [
    "endpoint_logger",
    "logtrace_endpoint",
    "setup_from_settings",
    "setup_loguru",
]
