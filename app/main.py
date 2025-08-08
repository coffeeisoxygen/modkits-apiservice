"""Main FastAPI Application."""

import time

from app.core.app_lifespan import app_lifespan
from app.core.app_middleware import LoggingMiddleware
from app.dependencies.dep_context import (
    ClientIpDep,
    MethodDep,
    PathDep,
    RequestIdDep,
    UserAgentDep,
)
from app.dependencies.dep_settings import AppConfig, AppConfigDep
from app.utils.log_setup import logger, logtrace_endpoint
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Modkits API Service",
    version="1.0.0",
    description="API service for Modkits, providing essential functionalities.",
    lifespan=app_lifespan,
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["General"])
@logtrace_endpoint("root")
async def read_root():
    """Root endpoint providing a welcome message."""
    return {"message": "Welcome to Modkits API Service!", "status": "ok"}


@app.get("/health", tags=["General"])
@logtrace_endpoint("health_check")
async def health_check():
    """Health check endpoint to verify service status."""
    return {
        "status": "healthy",
        "service": "modkits-apiservice",
        "timestamp": time.time(),
    }


@app.get("/info", tags=["Application"])
@logtrace_endpoint("app_info")
async def get_app_info(app_config: AppConfigDep) -> AppConfig:
    """Get application configuration information."""
    return app_config


@app.get("/test-sensitive", tags=["Testing"])
@logtrace_endpoint("test_sensitive")
async def test_sensitive_data():
    """Test endpoint for sensitive data redaction."""
    logger.info("Testing sensitive data logging:")
    logger.info("User password: mySecretPassword123")
    logger.info("API key: sk-1234567890abcdef")
    logger.info("Email: john.doe@company.com")
    logger.info("Phone: +628123456789")
    logger.info("Credit Card: 4532-1234-5678-9012")
    logger.info("Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")
    logger.info(
        "Secret key in JSON: {'secret': 'top-secret-data', 'public': 'visible'}"
    )

    return {
        "status": "test completed",
        "message": "Check logs to see sensitive data redaction in action",
    }


@app.get("/whoami", tags=["Debug"])
@logtrace_endpoint("whoami")
async def whoami(
    request_id: RequestIdDep,
    client_ip: ClientIpDep,
    user_agent: UserAgentDep,
    path: PathDep,
    method: MethodDep,
):
    """Show current request context (request_id, client_ip, user_agent, path, method)."""
    return {
        "request_id": request_id,
        "client_ip": client_ip,
        "user_agent": user_agent,
        "path": path,
        "method": method,
    }
