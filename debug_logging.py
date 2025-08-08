"""Simple test for the logging system."""

import sys

from loguru import logger

# Remove all handlers first
logger.remove()

# Add a simple stdout handler
logger.add(sys.stdout, level="DEBUG", format="{time} | {level} | {message}")

logger.info("Test message 1")
logger.debug("Test message 2")
logger.warning("Test message 3")

print("Direct print works")

# Now test our system
print("\n=== Testing our logging system ===")

from app.mlogg.environments import EnvironmentAwareSetup

env_setup = EnvironmentAwareSetup("development")
sink_configs = env_setup.get_sink_configs()

print(f"Found {len(sink_configs)} sink configurations:")
for i, config in enumerate(sink_configs):
    print(f"  {i + 1}. {config}")

# Test the full setup
from app.mlogg import setup_loguru

print("\n=== Testing full setup ===")
setup_loguru("development", enable_stream_redirection=False)
logger.info("After setup_loguru call")
