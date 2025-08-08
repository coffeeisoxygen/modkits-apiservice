"""Application lifespan event handler for FastAPI.

Setup loguru logging and handle startup/shutdown events using lifespan context.
"""

from contextlib import asynccontextmanager

from app.dependencies.dep_settings import get_app_config
from app.utils.log_setup import logger, setup_loguru

LEVEL = get_app_config().log_level
setup_loguru(level=LEVEL)


@asynccontextmanager
async def app_lifespan(app):  # noqa: ANN001, ARG001, RUF029
    """Lifespan context for FastAPI app: setup logging and log events."""
    # Logging already setup at module level
    logger.info("🚀 FastAPI application starting up (lifespan)")
    try:
        yield
    finally:
        logger.info("🛑 FastAPI application shutting down (lifespan)")
