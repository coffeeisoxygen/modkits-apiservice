import contextvars  # For thread-safe context
import time
import uuid

from app.dependencies.dep_settings import AppConfig, AppConfigDep
from app.utils.log_setup import logger
from fastapi import FastAPI, Request

app = FastAPI()

request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("request_id")


@app.middleware("http")
async def add_context_to_logs(request: Request, call_next):
    """Middleware untuk menambahkan request_id dan IP klien ke setiap log."""
    request_id = str(uuid.uuid4())
    client_ip: str | None = request.client.host if request.client else "unknown"

    # Set context variable supaya bisa diakses di endpoint
    request_id_ctx.set(request_id)

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
    logger.info("Handling root endpoint.")
    # You can access the bound data within your route handlers if needed
    current_request_id = request_id_ctx.get()
    return {"message": f"Hello, World! Request ID: {current_request_id}"}


@app.get("/info")
async def info(app_config: AppConfigDep) -> AppConfig:
    logger.bind(operation="get_app_config").info("Fetching application configuration")
    """Endpoint to get application configuration."""
    return app_config
