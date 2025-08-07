#!/usr/bin/env python3
"""Test script untuk sensitive data redaction dengan berbagai mode."""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from app.utils.log_setup import setup_loguru, enable_sensitive_logging
from loguru import logger


def test_sensitive_data_redaction():
    """Test sensitive data redaction functionality dengan berbagai mode."""

    modes = ["full", "partial", "hash"]

    # Test berbagai jenis data sensitif
    test_cases = [
        "User password: mySecretPassword123",
        "API key: sk-1234567890abcdef",
        "Email: john.doe@company.com",
        "Phone: +628123456789",
        "Credit Card: 4532-1234-5678-9012",
        "Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        "Login data: {'password': 'secret123', 'email': 'user@test.com'}",
        "Config: {'api_key': 'abc123def456', 'public_setting': 'visible'}",
        "IP Address: 192.168.1.100",
        "SSN: 123-45-6789",
        "URL with token: https://api.example.com/data?token=secret123",
        "Authorization: Bearer abc123def456ghi789",
        "Normal message without sensitive data",
        "Mixed: password=secret123 and email=user@test.com with IP 10.0.0.1",
    ]

    for mode in modes:
        print(f"\n{'=' * 60}")
        print(f"🛡️  TESTING REDACTION MODE: {mode.upper()}")
        print(f"{'=' * 60}")

        # Setup fresh logger untuk setiap mode
        setup_loguru()
        enable_sensitive_logging(redaction_mode=mode)

        print(f"\n📊 Testing {len(test_cases)} sensitive data cases:")

        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"Test {i}: {test_case}")

        print(f"\n✅ Mode '{mode}' test completed!")

    print(f"\n{'=' * 60}")
    print("🎉 ALL REDACTION MODES TESTED!")
    print("📊 Check the logs above to compare different redaction strategies")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    test_sensitive_data_redaction()
