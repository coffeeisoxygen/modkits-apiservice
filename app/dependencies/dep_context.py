# filepath: c:\Users\YOGA\project\otomax\modkits-apiservice\app\dependencies\dep_context.py
"""Dependencies for request context management."""

import contextvars
from typing import Annotated

from fastapi import Depends

# Context variables untuk menyimpan request context
request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("request_id")
client_ip_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("client_ip")


def get_request_context() -> tuple[str, str]:
    """Get current request context (request_id, client_ip).

    Returns:
        tuple[str, str]: (request_id, client_ip)
    """
    try:
        request_id = request_id_ctx.get()
        client_ip = client_ip_ctx.get()
    except LookupError:
        return "unknown", "unknown"
    else:
        return request_id, client_ip


def get_request_id() -> str:
    """Get current request ID."""
    try:
        return request_id_ctx.get()
    except LookupError:
        return "unknown"


def get_client_ip() -> str:
    """Get current client IP."""
    try:
        return client_ip_ctx.get()
    except LookupError:
        return "unknown"


# Type annotations untuk dependency injection
RequestContextDep = Annotated[tuple[str, str], Depends(get_request_context)]
RequestIdDep = Annotated[str, Depends(get_request_id)]
ClientIpDep = Annotated[str, Depends(get_client_ip)]
