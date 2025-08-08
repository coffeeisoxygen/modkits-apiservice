"""Log rotation utilities and size parsing."""

import datetime
import re
from typing import Any


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
    """Custom log rotator based on size and time."""

    def __init__(
        self, *, size: str | int = "500MB", at: datetime.time = datetime.time(0, 0, 0)
    ):
        now = datetime.datetime.now()
        self._size_limit = parse_size(size)
        self._time_limit = now.replace(hour=at.hour, minute=at.minute, second=at.second)
        if now >= self._time_limit:
            # The current time is already past the target time so it would rotate already.
            # Add one day to prevent an immediate rotation.
            self._time_limit += datetime.timedelta(days=1)

    def should_rotate(self, message: Any, file: Any) -> bool:
        """Check if log file should be rotated."""
        file.seek(0, 2)
        if file.tell() + len(message) > self._size_limit:
            return True
        excess = message.record["time"].timestamp() - self._time_limit.timestamp()
        if excess >= 0:
            elapsed_days = datetime.timedelta(seconds=excess).days
            self._time_limit += datetime.timedelta(days=elapsed_days + 1)
            return True
        return False


class RotationConfig:
    """Configuration for log rotation based on environment."""

    def __init__(self, environment: str = "development"):
        self.environment = environment.lower()

    def get_rotator(self) -> Rotator:
        """Get appropriate rotator for environment."""
        if self.environment == "production":
            # Production: Rotate daily at midnight or when size exceeds 100MB
            return Rotator(size="100MB", at=datetime.time(0, 0, 0))
        elif self.environment == "testing":
            # Testing: Smaller files, more frequent rotation
            return Rotator(size="10MB", at=datetime.time(0, 0, 0))
        else:  # development
            # Development: Larger files, less frequent rotation
            return Rotator(size="500MB", at=datetime.time(0, 0, 0))

    @property
    def compression(self) -> str | None:
        """Get compression setting for environment."""
        if self.environment == "production":
            return "zip"  # Compress in production to save space
        else:
            return None  # No compression in dev/test for easier debugging
