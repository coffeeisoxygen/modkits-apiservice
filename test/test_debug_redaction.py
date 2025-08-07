#!/usr/bin/env python3
"""Test script untuk debug sensitive data redaction."""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from app.utils.log_setup import setup_loguru, enable_sensitive_logging
from loguru import logger


def test_debug_redaction():
    """Test dengan debug untuk melihat cara kerja redaction."""

    print("🔧 Setting up logging...")
    setup_loguru()

    print("🛡️ Enabling sensitive data redaction with debug...")

    # Test redaction manual dulu
    from app.utils.log_setup import enable_sensitive_logging
    import re

    def test_redact_message(text: str) -> str:
        """Test redaction function."""
        message = text

        # Pattern sederhana untuk password
        pattern = r"(?i)(password|pwd|pass)\s*[:=]\s*['\"]?([^'\"\s,}]+)"
        message = re.sub(pattern, lambda m: f"{m.group(1)}: ********", message)

        # Pattern untuk email
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        message = re.sub(
            email_pattern,
            lambda m: f"{m.group(0)[:3]}***@{m.group(0).split('@')[1]}",
            message,
        )

        return message

    print("\n📊 Testing manual redaction:")

    test_cases = [
        "User password: mySecretPassword123",
        "Email: john.doe@company.com",
        "Normal message without sensitive data",
        "Mixed: password=secret123 and email=user@test.com",
    ]

    for i, test_case in enumerate(test_cases, 1):
        redacted = test_redact_message(test_case)
        print(f"Original {i}: {test_case}")
        print(f"Redacted {i}: {redacted}")
        print()

    print("🛡️ Now testing with Loguru integration...")
    enable_sensitive_logging("partial")

    print("\n📊 Testing with Loguru:")
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"Test {i}: {test_case}")


if __name__ == "__main__":
    test_debug_redaction()
