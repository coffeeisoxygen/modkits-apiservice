"""Dependencies for request context management."""

import contextvars
from typing import Annotated

from fastapi import Depends

# Context variables untuk menyimpan request context
request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("request_id")
client_ip_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("client_ip")
user_agent_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("user_agent")
path_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("path")
method_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("method")


def get_request_context() -> tuple[str, str, str, str, str]:
    """Get current request context (request_id, client_ip, user_agent, path, method).

    Returns:
        tuple[str, str, str, str, str]: (request_id, client_ip, user_agent, path, method)
    """
    try:
        request_id = request_id_ctx.get()
        client_ip = client_ip_ctx.get()
        user_agent = user_agent_ctx.get()
        path = path_ctx.get()
        method = method_ctx.get()
    except LookupError:
        return "unknown", "unknown", "unknown", "unknown", "unknown"
    else:
        return request_id, client_ip, user_agent, path, method


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


def get_user_agent() -> str:
    """Get current user agent."""
    try:
        return user_agent_ctx.get()
    except LookupError:
        return "unknown"


def get_path() -> str:
    """Get current request path."""
    try:
        return path_ctx.get()
    except LookupError:
        return "unknown"


def get_method() -> str:
    """Get current request method."""
    try:
        return method_ctx.get()
    except LookupError:
        return "unknown"


# Type annotations untuk dependency injection
RequestContextDep = Annotated[
    tuple[str, str, str, str, str], Depends(get_request_context)
]
RequestIdDep = Annotated[str, Depends(get_request_id)]
ClientIpDep = Annotated[str, Depends(get_client_ip)]
UserAgentDep = Annotated[str, Depends(get_user_agent)]
PathDep = Annotated[str, Depends(get_path)]
MethodDep = Annotated[str, Depends(get_method)]
