"""Exception handler registry for the application (manual style)."""

from collections.abc import Callable

from app.utils.exceptions import (
    AppExcpCaseError,
    ResourceNotFoundError,
    UnauthorizedError,
    ValidationError,
)
from app.utils.log_setup import logger
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def create_exception_handler(
    status_code: int, initial_detail: str
) -> Callable[[Request, AppExcpCaseError], JSONResponse]:
    """Create an exception handler for FastAPI.

    Args:
        status_code (int): HTTP status code to return.
        initial_detail (str): Default error message.

    Returns:
        Callable: An async exception handler function for FastAPI.
    """
    detail: dict[str, str] = {"message": initial_detail}

    async def exception_handler(_: Request, exc: AppExcpCaseError) -> JSONResponse:  # noqa: RUF029
        if exc.message:
            detail["message"] = exc.message

        if exc.name:
            detail["message"] = f"{detail['message']} [{exc.name}]"

        logger.exception(exc)
        return JSONResponse(
            status_code=status_code,
            content={"detail": detail["message"]},
        )

    return exception_handler  # type: ignore


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers to the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance.

    Returns:
        None
    """
    app.add_exception_handler(
        ResourceNotFoundError,
        create_exception_handler(
            ResourceNotFoundError.status_code,
            ResourceNotFoundError.default_message,
        ),  # pyright: ignore[reportArgumentType]
    )

    app.add_exception_handler(
        ValidationError,
        create_exception_handler(
            ValidationError.status_code,
            ValidationError.default_message,
        ),  # pyright: ignore[reportArgumentType]
    )

    app.add_exception_handler(
        UnauthorizedError,
        create_exception_handler(
            UnauthorizedError.status_code,
            UnauthorizedError.default_message,
        ),  # pyright: ignore[reportArgumentType]
    )

    app.add_exception_handler(
        AppExcpCaseError,
        create_exception_handler(
            AppExcpCaseError.status_code,
            AppExcpCaseError.default_message,
        ),  # pyright: ignore[reportArgumentType]
    )
