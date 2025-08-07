"""Main FastAPI Application."""

import time
import uuid
from collections.abc import Callable

from fastapi import FastAPI, Request
from app.utils.log_setup import setup_loguru, logger, simple_endpoint_logger
from app.dependencies.dep_settings import AppConfig, AppConfigDep
from app.dependencies.dep_context import request_id_ctx, client_ip_ctx, RequestIdDep, ClientIpDep

# Initialize and configure logging
setup_loguru(redaction=True, redaction_mode="hash")

app = FastAPI(
    title="Modkits API Service",
    version="1.0.0",
    description="API service for Modkits, providing essential functionalities."
)

@app.on_event("startup")
async def startup_event():
    """Log application startup."""
    logger.info("🚀 FastAPI application starting up")

@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    logger.info("🛑 FastAPI application shutting down")

@app.middleware("http")
async def logging_middleware(request: Request, call_next: Callable):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    client_ip = request.client.host if request.client else "unknown"

    # Set contextvars
    request_id_ctx.set(request_id)
    client_ip_ctx.set(client_ip)

    with logger.contextualize(request_id=request_id, client_ip=client_ip):
        logger.info(f"Request: {request.method} {request.url.path}")
        start_time = time.time()
        try:
            response = await call_next(request)
            execution_time = time.time() - start_time
            logger.info(
                f"Response: {response.status_code} | "
                f"Duration: {execution_time:.4f}s"
            )
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as e:
            logger.exception("Unhandled exception during request processing")
            raise e

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", tags=["General"])
@simple_endpoint_logger("root")
async def read_root():
    """Root endpoint providing a welcome message."""
    return {
        "message": "Welcome to Modkits API Service!",
        "status": "ok"
    }

@app.get("/health", tags=["General"])
@simple_endpoint_logger("health_check")
async def health_check():
    """Health check endpoint to verify service status."""
    return {
        "status": "healthy",
        "service": "modkits-apiservice",
        "timestamp": time.time()
    }

@app.get("/info", tags=["Application"])
@simple_endpoint_logger("app_info")
async def get_app_info(app_config: AppConfigDep) -> AppConfig:
    """Get application configuration information."""
    return app_config

@app.get("/test-sensitive", tags=["Testing"])
@simple_endpoint_logger("test_sensitive")
async def test_sensitive_data():
    """Test endpoint for sensitive data redaction."""
    logger.info("Testing sensitive data logging:")
    logger.info("User password: mySecretPassword123")
    logger.info("API key: sk-1234567890abcdef")
    logger.info("Email: john.doe@company.com")
    logger.info("Phone: +628123456789")
    logger.info("Credit Card: 4532-1234-5678-9012")
    logger.info("Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")
    logger.info("Secret key in JSON: {'secret': 'top-secret-data', 'public': 'visible'}")

    return {
        "status": "test completed",
        "message": "Check logs to see sensitive data redaction in action"
    }

@app.get("/whoami", tags=["Debug"])
@simple_endpoint_logger("whoami")
async def whoami(request_id: RequestIdDep, client_ip: ClientIpDep):
    """Show current request_id and client_ip from context."""
    return {
        "request_id": request_id,
        "client_ip": client_ip
    }
