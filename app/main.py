import asyncio
import time
import uuid
from collections.abc import Callable

from app.dependencies.dep_context import (
    client_ip_ctx,
    request_id_ctx,
)
from app.dependencies.dep_settings import AppConfig, AppConfigDep
from app.utils.log_setup import logger, track_endpoint_performance
from fastapi import FastAPI, Request

app = FastAPI()


@app.middleware("http")
async def add_context_to_logs(request: Request, call_next: Callable):
    """Middleware untuk menambahkan request_id dan IP klien ke setiap log."""
    request_id = str(uuid.uuid4())
    client_ip: str | None = request.client.host if request.client else "unknown"

    # Set context variable supaya bisa diakses di endpoint
    request_id_ctx.set(request_id)
    client_ip_ctx.set(client_ip)

    with logger.contextualize(request_id=request_id, client_ip=client_ip):
        start_time = time.time()
        logger.info(
            f"Incoming request: {request.method} {request.url.path} | IP: {client_ip}"
        )

        response = await call_next(request)

        process_time = time.time() - start_time
        logger.info(
            f"Outgoing response: {response.status_code} | Processed in {process_time:.4f}s | IP: {client_ip}"
        )
        return response


@app.get("/")
async def read_root():
    """Root endpoint dengan request tracking."""
    logger.info("Handling root endpoint.")
    # You can access the bound data within your route handlers if needed
    current_request_id = request_id_ctx.get()
    return {"message": f"Hello, World! Request ID: {current_request_id}"}


@app.get("/info")
async def info(app_config: AppConfigDep) -> AppConfig:
    """Endpoint to get application configuration."""
    logger.bind(operation="get_app_config").info("Fetching application configuration")
    return app_config


# Contoh endpoint menggunakan helper context manager
@app.get("/users")
async def get_users():
    """Endpoint dengan performance tracking menggunakan helper."""
    request_id = request_id_ctx.get()
    client_ip = client_ip_ctx.get()

    with track_endpoint_performance("get_users", request_id, client_ip) as log:
        log.info("Fetching users from database")
        # Simulasi delay
        await asyncio.sleep(0.1)
        log.info("Users fetched successfully")
        return {"users": ["admin", "user1"]}


# Contoh endpoint sederhana menggunakan dependency injection
@app.get("/profile")
async def get_user_profile():
    """Endpoint sederhana dengan context dari dependency."""
    request_id = request_id_ctx.get()
    client_ip = client_ip_ctx.get()

    with track_endpoint_performance("get_user_profile", request_id, client_ip) as log:
        log.info("Fetching user profile")

        # Simulasi business logic
        user_data = {
            "id": 1,
            "name": "admin",
            "role": "administrator",
            "created_at": "2024-01-01T00:00:00Z",
        }

        log.info("User profile fetched successfully", user_id=user_data["id"])
        return {"profile": user_data}


# Contoh endpoint dengan error handling
@app.get("/test-error")
async def test_error_endpoint():
    """Endpoint untuk testing error handling dengan context logging."""
    request_id = request_id_ctx.get()
    client_ip = client_ip_ctx.get()

    with track_endpoint_performance("test_error", request_id, client_ip) as log:
        log.info("Testing error handling")

        # Simulasi error
        if True:  # Sengaja error untuk testing
            log.error("Simulated error occurred")
            raise ValueError("This is a test error")

        return {"status": "success"}


@app.get("/simple")
async def simple_endpoint():
    """Endpoint sederhana untuk demonstrasi logging context."""
    request_id = request_id_ctx.get()
    client_ip = client_ip_ctx.get()

    log = logger.bind(request_id=request_id, client_ip=client_ip)
    log.info("Simple logging with context")
    return {"status": "ok"}
