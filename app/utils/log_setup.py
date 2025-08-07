"""setup loguru - Simple & Effective Endpoint Logging."""

import datetime
import functools
import hashlib
import logging
import os
import sys
import warnings
from collections.abc import Callable
from typing import Any, Literal
import re

import stackprinter
from loguru import logger

# ===========================================================================
# LOGURU LEVEL FOR EASIET TO PASS AS FUNCTION
Level = Literal["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]

# ===================================================================
# SENSITIVE DATA REDACTION
# ===================================================================

SENSITIVE_PATTERNS = {
    "password": r"(?i)(password|pwd|pass)\s*[:=]\s*['\"]?([^'\"\s,}]+)",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "phone": r"(\+62|0)\d{8,15}",
    "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
    "api_key": r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token)\s*[:=]\s*['\"]?([a-zA-Z0-9_-]{16,})",
    "token": r"(?i)(token|jwt|bearer)\s*[:=]?\s*['\"]?([a-zA-Z0-9_.-]{20,})",
    "secret_in_json": r"(?i)['\"]?(secret|password|token|key)['\"]?\s*:\s*['\"]([^'\"]+)['\"]",
    "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "url_with_token": r"https?://[^\s]*[?&](token|key|secret)=([^&\s]+)",
    "authorization_header": r"(?i)(authorization|bearer)\s*:\s*['\"]?([^'\"\s,}]+)"
}

SENSITIVE_KEYWORDS = [
    "password", "pwd", "pass", "secret", "token", "key",
    "api_key", "access_token", "refresh_token", "jwt",
    "credit_card", "card_number", "cvv", "pin",
    "ssn", "social_security", "auth", "authorization",
    "private_key", "public_key", "certificate", "cert"
]

def hash_value(value: str) -> str:
    """Generate SHA256 hash for sensitive values."""
    return f"SHA256:{hashlib.sha256(value.encode()).hexdigest()[:16]}..."

def redact_message(text: str, redaction_mode: str = "hash") -> str:
    """Redact sensitive data from a text message."""
    message = text
    for pattern_name, pattern in SENSITIVE_PATTERNS.items():
        # Check if pattern has at least 2 groups, else redact whole match
        compiled = re.compile(pattern)
        group_count = compiled.groups
        if group_count >= 2:
            if redaction_mode == "hash":
                message = compiled.sub(lambda m: f"{m.group(1)}: {hash_value(m.group(2))}", message)
            else:
                message = compiled.sub(lambda m: f"{m.group(1)}: ********", message)
        else:
            # For patterns like email, phone, etc. (no group 2)
            if redaction_mode == "hash":
                message = compiled.sub(lambda m: f"[REDACTED:{hash_value(m.group(0))}]", message)
            else:
                message = compiled.sub(lambda m: "[REDACTED]", message)

    for keyword in SENSITIVE_KEYWORDS:
        pattern = rf"(?i){keyword}\s*[:=]\s*['\"]?([^'\"\s,}}]+)"
        compiled = re.compile(pattern)
        if redaction_mode == "hash":
            message = compiled.sub(lambda m: f"{keyword}: {hash_value(m.group(1))}", message)
        else:
            message = compiled.sub(f"{keyword}: ********", message)
    return message

def sensitive_data_patcher(record):
    """Patcher function to redact sensitive data from log records."""
    # Use redaction_mode from logger extra if available, else default to 'hash'
    redaction_mode = record.get("extra", {}).get("redaction_mode", "hash")
    record["message"] = redact_message(record["message"], redaction_mode)

def patch_warnings_to_loguru():
    """Redirects Python warnings to loguru logger."""
    showwarning_ = warnings.showwarning
    def showwarning(message, *args, **kwargs):
        logger.opt(depth=2).warning(message)
        showwarning_(message, *args, **kwargs)
    warnings.showwarning = showwarning

def opener(file: str, flags: int) -> int:
    """Open a file with read/write by owner only permissions."""
    return os.open(file, flags, 0o600)

class StreamToLogger:
    """Redirects stdout/stderr to loguru logger."""
    def __init__(self, level: str = "INFO"):
        self._level = level
    def write(self, buffer: str):
        for line in buffer.rstrip().splitlines():
            logger.opt(depth=1).log(self._level, line.rstrip())
    def flush(self):
        pass

def parse_size(size: int | float | str) -> int:
    """Parse human-friendly size string to bytes."""
    if isinstance(size, (int, float)):
        return int(size)
    size = str(size).strip().upper()
    match = re.match(r"^(\d+(?:\.\d+)?)([KMGTP]?B)?$", size)
    if not match:
        raise ValueError(f"Invalid size format: {size}")
    num, unit = match.groups()
    num = float(num)
    unit_multipliers = {
        None: 1,
        "B": 1,
        "KB": 1024,
        "MB": 1024**2,
        "GB": 1024**3,
        "TB": 1024**4,
        "PB": 1024**5,
    }
    multiplier = unit_multipliers.get(unit, 1)
    return int(num * multiplier)

class Rotator:
    def __init__(self, *, size, at):
        now = datetime.datetime.now()
        self._size_limit = parse_size(size)
        self._time_limit = now.replace(hour=at.hour, minute=at.minute, second=at.second)
        if now >= self._time_limit:
            # The current time is already past the target time so it would rotate already.
            # Add one day to prevent an immediate rotation.
            self._time_limit += datetime.timedelta(days=1)

    def should_rotate(self, message, file):
        file.seek(0, 2)
        if file.tell() + len(message) > self._size_limit:
            return True
        excess = message.record["time"].timestamp() - self._time_limit.timestamp()
        if excess >= 0:
            elapsed_days = datetime.timedelta(seconds=excess).days
            self._time_limit += datetime.timedelta(days=elapsed_days + 1)
            return True
        return False

# Rotate file if over 500 MB or at midnight every day
rotator = Rotator(size="500MB", at=datetime.time(0, 0, 0))
# ===========================================================================
# LOGURU SETUP
# ===========================================================================

def exception_format(record: Any) -> str:
    """Custom format for exceptions with stackprinter."""
    if record["exception"] is not None:
        record["extra"]["stack"] = stackprinter.format(record["exception"])
        return "<green>{time}</green> | <level>{level}</level> | <level>{message}</level> | <cyan>{extra}</cyan>\n{extra[stack]}\n"
    return "<green>{time}</green> | <level>{level}</level> | <level>{message}</level> | <cyan>{extra}</cyan>\n"


def setup_loguru(
    level: str = "DEBUG",
    redaction: bool = True,
    redaction_mode: str = "hash",
    sink_stdout: bool = True,
    sink_stderr: bool = True,
    sink_file: str | None = None,

    ) -> None:
    """Setup loguru logger with safe default configurations."""
    logger.remove()  # Remove the default logger

    if not sink_stdout and not sink_stderr:
        raise RuntimeError("At least one of sink_stdout or sink_stderr must be True for logger setup.")

    if sink_stdout:
        logger.add(
            sink=sys.stdout,
            level=level,
            format="<green>{time}</green> | <level>{level}</level> | <level>{message}</level> | <cyan>{extra}</cyan>",
            backtrace=True,
            diagnose=True,
        )

    if sink_stderr:
        logger.add(
            sink=sys.stderr,
            level="ERROR",
            format=exception_format,
            backtrace=True,
            diagnose=True,
        )
    if sink_file:
        logger.add(
            sink=sink_file,
            level=level,
            format="<green>{time}</green> | <level>{level}</level> | <level>{message}</level> | <cyan>{extra}</cyan>",
            rotation=rotator.should_rotate,
            compression="zip",
            serialize=True,
            enqueue=True,
            encoding="utf-8",
            mode="a",
            backtrace=True,
            diagnose=False,
        )

    if redaction:
        logger.configure(patcher=sensitive_data_patcher)
        logger.info(f"🛡️ Sensitive data redaction enabled (mode: {redaction_mode})")

    # Intercept standard logging messages and send to loguru
    class InterceptHandler(logging.Handler):
        """Intercepts standard logging messages and sends them to loguru."""
        def emit(self, record: Any) -> None:
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno
            logger.opt(depth=6, exception=record.exc_info).log(
                level, record.getMessage()
            )

    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    patch_warnings_to_loguru()
    sys.stdout = StreamToLogger("INFO")
    sys.stderr = StreamToLogger("ERROR")

# redirecting setup

# ===========================================================================
# DECORATORS & CONTEXT MANAGERS
# ===========================================================================

def simple_endpoint_logger(endpoint_name: str | None = None) -> Callable:
    """Decorator to log the start and end of an endpoint function."""
    def decorator(func: Callable) -> Callable:
        name = endpoint_name or func.__name__
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger.info(f"Executing endpoint: '{name}'")
            result = await func(*args, **kwargs)
            logger.info(f"Finished endpoint: '{name}'")
            return result
        return wrapper
    return decorator

# ===========================================================================
# ALIASES & UTILITIES
# ===========================================================================

endpoint_logger = simple_endpoint_logger
