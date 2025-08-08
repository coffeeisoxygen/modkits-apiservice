"""Log formatters for different environments and use cases."""

from typing import Any

import stackprinter

# Base formats
FORMAT_PRODUCTION = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> | <level>{message}</level> | <cyan>{extra}</cyan>"

FORMAT_DEVELOPMENT = "<level>{level.name}</level>: <magenta>{name}:{function}:{line}</magenta> | {message} | {extra}"

FORMAT_DEVELOPMENT_EXCEPTION = "<level>{level.name}</level>: <magenta>{module}:{name}:{function}:{line}>{process}</magenta> | {message} | {extra} | <red>{exception}</red>"

FORMAT_TESTING = "<level>{level.name}</level>: <cyan>{name}</cyan> | {message}"

FORMAT_MINIMAL = "{level}: {message}"

FORMAT_JSON = "{time} | {level} | {name} | {message} | {extra}"


def exception_format(record: Any) -> str:
    """Custom format for exceptions with stackprinter."""
    if record["exception"] is not None:
        record["extra"]["stack"] = stackprinter.format(record["exception"])
        return "<green>{time}</green> | <level>{level}</level> | <level>{message}</level> | <cyan>{extra}</cyan>\n{extra[stack]}\n"
    return "<green>{time}</green> | <level>{level}</level> | <level>{message}</level> | <cyan>{extra}</cyan>\n"


class FormatConfig:
    """Configuration for log formats based on environment."""

    def __init__(self, environment: str = "development"):
        self.environment = environment.lower()

    @property
    def stdout_format(self) -> str:
        """Format for stdout output."""
        if self.environment == "production":
            return FORMAT_PRODUCTION
        elif self.environment == "testing":
            return FORMAT_TESTING
        else:  # development
            return FORMAT_DEVELOPMENT

    @property
    def stderr_format(self) -> str:
        """Format for stderr output (errors)."""
        if self.environment == "production":
            return FORMAT_PRODUCTION
        elif self.environment == "testing":
            return FORMAT_TESTING
        else:  # development
            return FORMAT_DEVELOPMENT_EXCEPTION

    @property
    def file_format(self) -> str:
        """Format for file output."""
        if self.environment == "testing":
            return FORMAT_TESTING
        else:
            return FORMAT_PRODUCTION  # Same for prod and dev file logging
