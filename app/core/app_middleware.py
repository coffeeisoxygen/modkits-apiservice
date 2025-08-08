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
        request_id, client_ip, user_agent, path, method = self._extract_request_info(
            request
        )
        self._set_context_vars(request_id, client_ip, user_agent, path, method)

        request_logger = logger.bind(
            operation="request",
            request_id=request_id,
            client_ip=client_ip,
            # user_agent=user_agent,
            path=path,
            method=method,
        )

        with request_logger.contextualize():
            request_logger.debug(f"Request: {method} {path}")
            start_time = time.time()
            try:
                response = await call_next(request)
                self._log_response(response, start_time, request_logger)
                response.headers["X-Request-ID"] = request_id
            except Exception:
                self._log_exception(method, path, start_time, request_logger)
                raise
            else:
                return response

    def _extract_request_info(self, request: Request) -> tuple[str, str, str, str, str]:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        path = request.url.path
        method = request.method
        return request_id, client_ip, user_agent, path, method

    def _set_context_vars(
        self,
        request_id: str,
        client_ip: str,
        user_agent: str,
        path: str,
        method: str,
    ) -> None:
        request_id_ctx.set(request_id)
        client_ip_ctx.set(client_ip)
        user_agent_ctx.set(user_agent)
        path_ctx.set(path)
        method_ctx.set(method)

    def _log_response(
        self,
        response: Response,
        start_time: float,
        logger_instance,  # noqa: ANN001
    ) -> None:
        execution_time = time.time() - start_time
        logger_instance.debug(
            f"Response: {response.status_code} | Duration: {execution_time:.4f}s"
        )

    def _log_exception(
        self,
        method: str,
        path: str,
        start_time: float,
        logger_instance,  # noqa: ANN001
    ) -> None:
        logger_instance.exception(f"Unhandled exception during {method} {path}")
        execution_time = time.time() - start_time
        logger_instance.error(f"Failed request duration: {execution_time:.4f}s")
