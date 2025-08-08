"""Security utilities for sensitive data redaction in logs."""

import hashlib
import re
from typing import Any

# Sensitive data patterns
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
    "authorization_header": r"(?i)(authorization|bearer)\s*:\s*['\"]?([^'\"\s,}]+)",
}

SENSITIVE_KEYWORDS = [
    "password",
    "pwd",
    "pass",
    "secret",
    "token",
    "key",
    "api_key",
    "access_token",
    "refresh_token",
    "jwt",
    "credit_card",
    "card_number",
    "cvv",
    "pin",
    "ssn",
    "social_security",
    "auth",
    "authorization",
    "private_key",
    "public_key",
    "certificate",
    "cert",
]


def hash_value(value: str) -> str:
    """Generate SHA256 hash for sensitive values."""
    return f"SHA256:{hashlib.sha256(value.encode()).hexdigest()[:16]}..."


def redact_message(text: str, redaction_mode: str = "hash") -> str:
    """Redact sensitive data from a text message.

    Args:
        text: The text to redact sensitive data from
        redaction_mode: Either 'hash' to show hash or 'mask' to show asterisks

    Returns:
        Text with sensitive data redacted
    """
    message = text

    # Process regex patterns
    for pattern in SENSITIVE_PATTERNS.values():
        compiled = re.compile(pattern)
        group_count = compiled.groups

        if group_count >= 2:
            if redaction_mode == "hash":
                message = compiled.sub(
                    lambda m: f"{m.group(1)}: {hash_value(m.group(2))}", message
                )
            else:
                message = compiled.sub(lambda m: f"{m.group(1)}: ********", message)
        else:
            # For patterns like email, phone, etc. (no group 2)
            if redaction_mode == "hash":
                message = compiled.sub(
                    lambda m: f"[REDACTED:{hash_value(m.group(0))}]", message
                )
            else:
                message = compiled.sub(lambda m: "[REDACTED]", message)  # noqa: ARG005

    # Process keywords
    for keyword in SENSITIVE_KEYWORDS:
        pattern = rf"(?i){keyword}\s*[:=]\s*['\"]?([^'\"\s,}}]+)"
        compiled = re.compile(pattern)
        if redaction_mode == "hash":
            message = compiled.sub(
                lambda m, kw=keyword: f"{kw}: {hash_value(m.group(1))}", message
            )
        else:
            message = compiled.sub(f"{keyword}: ********", message)

    return message


def sensitive_data_patcher(record: Any) -> None:
    """Patcher function to redact sensitive data from log records."""
    # Use redaction_mode from logger extra if available, else default to 'hash'
    redaction_mode = record.get("extra", {}).get("redaction_mode", "hash")
    record["message"] = redact_message(record["message"], redaction_mode)


class SecurityConfig:
    """Configuration for security features in logging."""

    def __init__(
        self,
        enable_redaction: bool = True,
        redaction_mode: str = "hash",
        environment: str = "development",
    ):
        self.enable_redaction = enable_redaction
        self.redaction_mode = redaction_mode
        self.environment = environment.lower()

    @property
    def should_redact(self) -> bool:
        """Determine if redaction should be enabled based on environment."""
        # Always redact in production, configurable in dev/test
        if self.environment == "production":
            return True
        return self.enable_redaction

    @property
    def effective_redaction_mode(self) -> str:
        """Get effective redaction mode based on environment."""
        # Use hash mode in production for audit trails, allow mask in dev
        if self.environment == "production":
            return "hash"
        return self.redaction_mode
