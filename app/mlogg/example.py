"""Example usage of the new logging system.

This file demonstrates how to use the refactored logging system
with environment-aware configurations.
"""

import asyncio

from app.config.settings import Settings
from app.mlogg import logtrace_endpoint, setup_from_settings, setup_loguru
from loguru import logger


def example_basic_setup():
    """Example 1: Basic environment-aware setup."""
    print("\n=== Example 1: Basic Setup ===")

    # Development setup
    setup_loguru("development")
    logger.info("This is development logging")
    logger.debug("Debug information visible in dev mode")

    # Production setup
    setup_loguru("production")
    logger.warning("This is production logging")
    logger.debug("Debug information hidden in production")  # Won't show


def example_settings_integration():
    """Example 2: Integration with application settings."""
    print("\n=== Example 2: Settings Integration ===")

    # Load settings and setup logging
    settings = Settings()  # type: ignore
    setup_from_settings(settings)

    logger.info(f"Logging setup for environment: {settings.environment}")
    logger.success("Settings-based logging initialized successfully!")


def example_custom_config():
    """Example 3: Custom configuration override."""
    print("\n=== Example 3: Custom Configuration ===")

    # Override some defaults
    custom_config = {
        "log_level": "INFO",
        "enable_file_logging": False,  # Disable file logging
        "enable_redaction": False,  # Disable redaction for this example
    }

    setup_loguru("development", custom_config)
    logger.info("Custom configuration applied")
    logger.debug("This debug message won't show (level is INFO)")


@logtrace_endpoint()
async def example_endpoint():
    """Example 4: Endpoint tracing decorator."""
    logger.info("Processing request...")
    # Simulate some work
    await asyncio.sleep(0.1)
    logger.info("Request processed successfully")
    return {"status": "success"}


@logtrace_endpoint("custom_endpoint_name")
def another_endpoint():
    """Example 5: Custom endpoint name."""
    logger.info("Custom named endpoint")
    return {"message": "Hello from custom endpoint"}


def example_sensitive_data():
    """Example 6: Sensitive data redaction."""
    print("\n=== Example 6: Sensitive Data Redaction ===")

    # Setup with redaction enabled
    setup_loguru("development", {"enable_redaction": True, "redaction_mode": "hash"})

    # This will be automatically redacted
    logger.info("User login with password: secret123")
    logger.info("API key: sk-1234567890abcdef")
    logger.info("Email: user@example.com")

    # Setup with mask mode
    setup_loguru("development", {"enable_redaction": True, "redaction_mode": "mask"})
    logger.info("Credit card: 1234-5678-9012-3456")


def example_environment_differences():
    """Example 7: Show differences between environments."""
    print("\n=== Example 7: Environment Differences ===")

    environments = ["development", "testing", "production"]

    for env in environments:
        print(f"\n--- {env.upper()} ENVIRONMENT ---")
        setup_loguru(env)

        logger.trace("Trace level message")
        logger.debug("Debug level message")
        logger.info(f"Info message from {env}")
        logger.warning(f"Warning from {env}")
        logger.error(f"Error from {env}")


async def main():
    """Run all examples."""
    print("🚀 New Logging System Examples")
    print("=" * 50)

    example_basic_setup()
    example_settings_integration()
    example_custom_config()
    example_sensitive_data()
    example_environment_differences()

    print("\n=== Example 4 & 5: Endpoint Tracing ===")
    await example_endpoint()
    another_endpoint()  # Non-async call

    print("\n✅ All examples completed!")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
