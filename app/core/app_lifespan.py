"""Application lifespan event handler for FastAPI.

Setup loguru logging and handle startup/shutdown events using lifespan context.
"""

from contextlib import asynccontextmanager

from app.utils.log_setup import logger, setup_loguru


@asynccontextmanager
async def app_lifespan(app):  # noqa: ANN001, ARG001, RUF029
    """Lifespan context for FastAPI app: setup logging and log events."""
    # Setup logging from settings (auto profile + override support)

    setup_loguru()
    logger.info("🚀 FastAPI application starting up (lifespan)")
    try:
        yield
    finally:
        logger.info("🛑 FastAPI application shutting down (lifespan)")
