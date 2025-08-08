"""Core logging utilities and base functionality."""

import logging
import os
import sys
import warnings
from pathlib import Path
from typing import Any

from loguru import logger


def opener(file: str, flags: int) -> int:
    """Open a file with read/write by owner only permissions."""
    return os.open(file, flags, 0o600)


class StreamToLogger:
    """Redirects stdout/stderr to loguru logger."""

    def __init__(self, level: str = "INFO"):
        self._level = level

    def write(self, buffer: str):
        for line in buffer.rstrip().splitlines():
            logger.opt(depth=1).log(self._level, line.rstrip())

    def flush(self):
        pass


class InterceptHandler(logging.Handler):
    """Intercepts standard logging messages and sends them to loguru."""

    def emit(self, record: Any) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


def patch_warnings_to_loguru():
    """Redirects Python warnings to loguru logger."""
    showwarning_ = warnings.showwarning

    def showwarning(message: Any, *args: Any, **kwargs: Any):
        logger.opt(depth=2).warning(message)
        showwarning_(message, *args, **kwargs)

    warnings.showwarning = showwarning


def configure_uvicorn_logging():
    """Configure Uvicorn logging to use loguru.

    This function should be called before Uvicorn starts to ensure
    all Uvicorn logs are intercepted and formatted consistently.
    """
    # Intercept Uvicorn loggers
    uvicorn_loggers = (
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "uvicorn.asgi",
    )

    # Replace all handlers with InterceptHandler
    for logger_name in uvicorn_loggers:
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers = [InterceptHandler()]
        uvicorn_logger.propagate = False

    # Set log level for uvicorn.access
    access_logger = logging.getLogger("uvicorn.access")
    access_logger.setLevel(logging.INFO)

    logger.debug("🔄 Uvicorn logging configured to use loguru")


def setup_stream_redirection():
    """Redirect stdout/stderr to loguru."""
    sys.stdout = StreamToLogger("INFO")
    sys.stderr = StreamToLogger("ERROR")


def setup_stdlib_integration():
    """Setup integration with stdlib logging and warnings."""
    # Intercept standard logging messages and send to loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    patch_warnings_to_loguru()
    configure_uvicorn_logging()


def ensure_log_directory(file_path: str | Path) -> Path:
    """Ensure log directory exists."""
    file_path = Path(file_path)
    if not file_path.parent.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
    return file_path
