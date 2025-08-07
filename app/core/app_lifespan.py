"""Application lifespan event handler for FastAPI.

Setup loguru logging and handle startup/shutdown events using lifespan context.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.dependencies.dep_settings import get_log_settings
from app.utils.log_setup import setup_loguru, logger

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    """Lifespan context for FastAPI app: setup logging and log events."""
    # Setup logging from settings (auto profile + override support)
    log_settings = get_log_settings()
    setup_loguru(
        level=log_settings.log_level,
        redaction=log_settings.log_redaction,
        redaction_mode=log_settings.log_redaction_mode,
        sink_stdout=log_settings.log_sink_stdout,
        sink_stderr=log_settings.log_sink_stderr,
        sink_file=log_settings.log_sink_file,
        serialize=log_settings.log_serialization,
        enqueue=log_settings.log_enqueue,
        diagnose=log_settings.log_diagnose,
    )
    logger.info("🚀 FastAPI application starting up (lifespan)")
    try:
        yield
    finally:
        logger.info("🛑 FastAPI application shutting down (lifespan)")
