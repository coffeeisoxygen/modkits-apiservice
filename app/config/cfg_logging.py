"""Logging configuration models."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, field_validator, model_validator


class LogLevel(StrEnum):
    """Valid log levels."""

    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class RedactionMode(StrEnum):
    """Redaction modes for sensitive data."""

    HASH = "hash"
    MASK = "mask"


class LogSettings(BaseModel):
    """Log settings configuration with environment awareness."""

    # Basic settings
    log_level: LogLevel = LogLevel.DEBUG
    log_redaction: bool = True
    log_redaction_mode: RedactionMode = RedactionMode.HASH

    # Sink settings
    log_sink_stdout: bool = True
    log_sink_stderr: bool = True
    log_sink_file: str | None = None

    # Advanced settings
    log_serialization: bool = False
    log_enqueue: bool = True
    log_diagnose: bool = False
    log_format: str | None = None

    # Environment override (if provided, will use environment-specific defaults)
    log_environment: str | None = None

    @field_validator("log_level", mode="before")
    @classmethod
    def validate_log_level(cls, value: Any) -> LogLevel:
        """Validate and convert log level."""
        if isinstance(value, LogLevel):
            return value
        if isinstance(value, str):
            try:
                return LogLevel(value.upper())
            except ValueError:
                valid_levels = [level.value for level in LogLevel]
                raise ValueError(
                    f"Invalid log level: {value}. Must be one of: {valid_levels}"
                ) from None
        raise ValueError(f"Log level must be string or LogLevel, got {type(value)}")

    @field_validator("log_redaction_mode", mode="before")
    @classmethod
    def validate_redaction_mode(cls, value: Any) -> RedactionMode:
        """Validate and convert redaction mode."""
        if isinstance(value, RedactionMode):
            return value
        if isinstance(value, str):
            try:
                return RedactionMode(value.lower())
            except ValueError:
                valid_modes = [mode.value for mode in RedactionMode]
                raise ValueError(
                    f"Invalid redaction mode: {value}. Must be one of: {valid_modes}"
                ) from None
        raise ValueError(
            f"Redaction mode must be string or RedactionMode, got {type(value)}"
        )

    @model_validator(mode="after")
    def validate_log_settings(self) -> "LogSettings":
        """Validate log settings after model creation."""
        if not self.log_sink_stdout and not self.log_sink_stderr:
            raise ValueError(
                "At least one log sink must be enabled (stdout or stderr)."
            )
        return self

    def to_mlogg_config(self) -> dict[str, Any]:
        """Convert to config dict for mlogg setup."""
        return {
            "log_level": self.log_level.value,
            "enable_redaction": self.log_redaction,
            "redaction_mode": self.log_redaction_mode.value,
            "enable_stdout": self.log_sink_stdout,
            "enable_stderr": self.log_sink_stderr,
            "file_path": self.log_sink_file,
            "serialize": self.log_serialization,
            "enqueue": self.log_enqueue,
            "diagnose": self.log_diagnose,
        }
