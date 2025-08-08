from pydantic import BaseModel, field_validator, model_validator

valid_levels = [
    "TRACE",
    "DEBUG",
    "INFO",
    "SUCCESS",
    "WARNING",
    "ERROR",
    "CRITICAL",
]


class LogSettings(BaseModel):
    """Log settings configuration."""

    log_level: str
    log_redaction: bool
    log_redaction_mode: str
    log_sink_stdout: bool
    log_sink_stderr: bool
    log_sink_file: str | None = None  # Make optional with None default
    log_serialization: bool
    log_enqueue: bool
    log_diagnose: bool
    log_format: str | None = None  # Optional

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        """Validate log level."""
        if value not in valid_levels:
            raise ValueError(
                f"Invalid log level: {value}. Must be one of: {valid_levels}"
            )
        return value

    @model_validator(mode="after")
    def validate_log_settings(self) -> "LogSettings":
        """Validate log settings after model creation."""
        if not self.log_sink_stdout and not self.log_sink_stderr:
            raise ValueError(
                "At least one log sink must be enabled (stdout or stderr)."
            )
        return self
