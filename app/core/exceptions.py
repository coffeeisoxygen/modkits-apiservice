"""Base exceptions for the application."""

from app.dependencies.dep_settings import get_app_config

APP_NAME = get_app_config().service


class AppExcpCaseError(Exception):
    """Base exception for our application."""

    default_message: str = "An application error occurred."
    status_code: int = 500

    def __init__(
        self,
        message: str | None = None,
        name: str | None = APP_NAME,
    ):
        self.message = message or self.default_message
        self.name = name
        super().__init__(f"[{self.status_code}] {self.message}")


class ResourceNotFoundError(AppExcpCaseError):
    default_message = "Resource not found."
    status_code = 404


class ValidationError(AppExcpCaseError):
    default_message = "Validation failed."
    status_code = 400


class UnauthorizedError(AppExcpCaseError):
    default_message = "Unauthorized access."
    status_code = 401
