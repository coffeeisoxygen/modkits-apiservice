"""Environment-specific logging configurations."""

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.mlogg.formatters import FormatConfig
from app.mlogg.rotation import RotationConfig
from app.mlogg.security import SecurityConfig


@dataclass
class LogEnvironmentConfig:
    """Configuration for a specific logging environment."""

    name: str
    log_level: str
    enable_file_logging: bool
    file_path: str | None
    enable_stdout: bool
    enable_stderr: bool
    enable_redaction: bool
    redaction_mode: str
    serialize: bool
    enqueue: bool
    diagnose: bool

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.enable_stdout and not self.enable_stderr:
            raise ValueError("At least one of stdout or stderr must be enabled")

        if self.enable_file_logging and not self.file_path:
            raise ValueError("file_path must be provided when file logging is enabled")


class EnvironmentConfigs:
    """Predefined configurations for different environments."""

    @staticmethod
    def development() -> LogEnvironmentConfig:
        """Development environment configuration."""
        return LogEnvironmentConfig(
            name="development",
            log_level="DEBUG",
            enable_file_logging=True,
            file_path="logs/dev/app.log",
            enable_stdout=True,
            enable_stderr=True,
            enable_redaction=False,  # Disable in dev for easier debugging
            redaction_mode="mask",
            serialize=False,
            enqueue=True,
            diagnose=True,  # Enable detailed diagnostics in dev
        )

    @staticmethod
    def testing() -> LogEnvironmentConfig:
        """Testing environment configuration."""
        return LogEnvironmentConfig(
            name="testing",
            log_level="INFO",
            enable_file_logging=True,
            file_path="logs/test/app.log",
            enable_stdout=False,  # Reduce noise in tests
            enable_stderr=True,  # Only errors to stderr
            enable_redaction=True,
            redaction_mode="mask",
            serialize=False,
            enqueue=False,  # Synchronous logging for tests
            diagnose=False,
        )

    @staticmethod
    def production() -> LogEnvironmentConfig:
        """Production environment configuration."""
        return LogEnvironmentConfig(
            name="production",
            log_level="WARNING",
            enable_file_logging=True,
            file_path="logs/prod/app.log",
            enable_stdout=False,  # No stdout in production
            enable_stderr=True,  # Only errors
            enable_redaction=True,  # Always redact in production
            redaction_mode="hash",  # Use hash for audit trails
            serialize=True,  # JSON format for log analysis
            enqueue=True,  # Async logging for performance
            diagnose=False,  # No diagnostics in production
        )

    @classmethod
    def get_config(cls, environment: str) -> LogEnvironmentConfig:
        """Get configuration for specified environment."""
        env = environment.lower()
        if env == "development":
            return cls.development()
        elif env == "testing":
            return cls.testing()
        elif env == "production":
            return cls.production()
        else:
            raise ValueError(f"Unknown environment: {environment}")


class EnvironmentAwareSetup:
    """Setup logging based on environment configuration."""

    def __init__(self, environment: str = "development"):
        self.environment = environment.lower()
        self.config = EnvironmentConfigs.get_config(self.environment)
        self.format_config = FormatConfig(self.environment)
        self.security_config = SecurityConfig(
            enable_redaction=self.config.enable_redaction,
            redaction_mode=self.config.redaction_mode,
            environment=self.environment,
        )
        self.rotation_config = RotationConfig(self.environment)

    @property
    def log_file_path(self) -> Path | None:
        """Get log file path if file logging is enabled."""
        if self.config.enable_file_logging and self.config.file_path:
            return Path(self.config.file_path)
        return None

    def get_sink_configs(self) -> list[dict[str, Any]]:
        """Get list of sink configurations for loguru."""
        sinks = []

        # stdout sink
        if self.config.enable_stdout:
            sinks.append({
                "sink": sys.stdout,
                "level": self.config.log_level,
                "format": self.format_config.stdout_format,
                "backtrace": True,
                "diagnose": self.config.diagnose,
                "serialize": False,  # stdout is never serialized
                "enqueue": False,  # stdout is synchronous
                "colorize": True,
            })

        # stderr sink
        if self.config.enable_stderr:
            sinks.append({
                "sink": sys.stderr,
                "level": "ERROR",
                "format": self.format_config.stderr_format,
                "backtrace": True,
                "diagnose": self.config.diagnose,
                "serialize": False,  # stderr is never serialized
                "enqueue": True,  # stderr can be async
                "colorize": True,
            })

        # file sink
        if self.config.enable_file_logging and self.log_file_path:
            rotator = self.rotation_config.get_rotator()
            sinks.append({
                "sink": str(self.log_file_path),
                "level": self.config.log_level,
                "format": self.format_config.file_format,
                "rotation": rotator.should_rotate,
                "compression": self.rotation_config.compression,
                "serialize": self.config.serialize,
                "enqueue": self.config.enqueue,
                "encoding": "utf-8",
                "mode": "a",
                "backtrace": True,
                "diagnose": False,  # Never diagnose in file logs
                "colorize": False,  # No colors in file logs
            })

        return sinks
