# filepath: c:\Users\YOGA\project\otomax\modkits-apiservice\app\examples\with_context_helper.py
"""Contoh penggunaan helper untuk context logging dan performance tracking."""

import asyncio

from app.dependencies.dep_context import (
    RequestContextDep,
    client_ip_ctx,
    request_id_ctx,
)
from app.utils.log_setup import (
    bind_request_context,
    endpoint_logger,
    track_endpoint_performance,
)
from fastapi import APIRouter

router = APIRouter(prefix="/examples", tags=["examples"])


# Metode 1: Manual dengan track_endpoint_performance
@router.get("/manual-tracking")
async def manual_tracking():
    """Contoh manual performance tracking dengan context."""
    request_id = request_id_ctx.get()
    client_ip = client_ip_ctx.get()

    with track_endpoint_performance("manual_tracking", request_id, client_ip) as log:
        log.info("Starting manual tracking process")

        # Simulasi business logic
        await asyncio.sleep(0.05)
        log.info("Processing data")

        # Simulasi database query
        await asyncio.sleep(0.1)
        log.info("Database query completed")

        return {"status": "success", "method": "manual_tracking"}


# Metode 2: Menggunakan bind_request_context untuk logging sederhana
@router.get("/simple-logging")
async def simple_logging():
    """Contoh simple logging dengan context binding."""
    request_id = request_id_ctx.get()
    client_ip = client_ip_ctx.get()

    log = bind_request_context(request_id, client_ip)

    log.info("Simple logging example started")

    # Business logic
    result = {"data": "example", "processed_at": "2024-01-01"}

    log.info("Processing completed", result_count=len(result))
    return result


# Metode 3: Menggunakan dependency injection
@router.get("/with-dependency")
async def with_dependency(context: RequestContextDep):
    """Contoh menggunakan dependency injection untuk context."""
    request_id, client_ip = context

    with track_endpoint_performance("with_dependency", request_id, client_ip) as log:
        log.info("Using dependency injection for context")

        # Simulasi complex processing
        data = []
        for i in range(3):
            await asyncio.sleep(0.02)
            data.append(f"item_{i}")
            log.debug(f"Processed item {i}")

        log.info("All items processed", total_items=len(data))
        return {"items": data}


# Metode 4: Menggunakan decorator (experimental)
@router.get("/with-decorator")
@endpoint_logger("user_data_endpoint")
async def with_decorator():
    """Contoh menggunakan decorator untuk automatic logging."""
    # Decorator akan otomatis handle context dan performance tracking
    # log parameter akan tersedia dalam kwargs jika diperlukan

    await asyncio.sleep(0.08)
    return {"message": "This endpoint uses decorator for logging"}


# Contoh error handling dengan context
@router.get("/error-handling")
async def error_handling_example():
    """Contoh error handling dengan context logging."""
    request_id = request_id_ctx.get()
    client_ip = client_ip_ctx.get()

    with track_endpoint_performance("error_handling", request_id, client_ip) as log:
        log.info("Testing error handling")

        try:
            # Simulasi proses yang bisa error
            result = 10 / 0
            return {"result": result}
        except ZeroDivisionError as e:
            log.error(f"Mathematical error occurred: {e!s}")
            return {"error": "Division by zero", "status": "handled"}
        except Exception as e:
            log.error(f"Unexpected error: {e!s}")
            raise


# Contoh untuk operasi yang memerlukan multiple steps
@router.get("/multi-step")
async def multi_step_process():
    """Contoh proses multi-step dengan detailed logging."""
    request_id = request_id_ctx.get()
    client_ip = client_ip_ctx.get()

    with track_endpoint_performance("multi_step_process", request_id, client_ip) as log:
        log.info("Starting multi-step process")

        # Step 1: Validation
        log.info("Step 1: Validating input")
        await asyncio.sleep(0.03)

        # Step 2: Data processing
        log.info("Step 2: Processing data")
        await asyncio.sleep(0.05)

        # Step 3: Database operations
        log.info("Step 3: Database operations")
        await asyncio.sleep(0.07)

        # Step 4: Response preparation
        log.info("Step 4: Preparing response")
        await asyncio.sleep(0.02)

        response = {"steps_completed": 4, "status": "success", "request_id": request_id}

        log.info(
            "Multi-step process completed successfully",
            total_steps=response["steps_completed"],
        )

        return response
