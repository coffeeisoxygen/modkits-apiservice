"""HTTP middleware for request logging and context management."""

import time
import uuid
from collections.abc import Callable

from app.dependencies.dep_context import (
    client_ip_ctx,
    method_ctx,
    path_ctx,
    request_id_ctx,
    user_agent_ctx,
)
from app.utils.log_setup import logger
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request logging and context variable management."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request, set context variables, and log request/response details.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler

        Returns:
            The HTTP response
        """
        # Extract request information
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        path = request.url.path
        method = request.method

        # Set context variables for dependency injection
        request_id_ctx.set(request_id)
        client_ip_ctx.set(client_ip)
        user_agent_ctx.set(user_agent)
        path_ctx.set(path)
        method_ctx.set(method)

        # Log with context
        with logger.contextualize(
            request_id=request_id,
            client_ip=client_ip,
            user_agent=user_agent,
            path=path,
            method=method,
        ):
            # Log request
            logger.debug(f"Request: {method} {path}")
            start_time = time.time()

            try:
                # Process request
                response = await call_next(request)

                # Log response
                execution_time = time.time() - start_time
                logger.debug(
                    f"Response: {response.status_code} | "
                    f"Duration: {execution_time:.4f}s"
                )

                # Add request ID to response headers
                response.headers["X-Request-ID"] = request_id
            except Exception:
                # Log exception with full context
                logger.exception(f"Unhandled exception during {method} {path}")
                execution_time = time.time() - start_time
                logger.error(f"Failed request duration: {execution_time:.4f}s")

                # Re-raise for FastAPI exception handlers
                raise
            else:
                return response
