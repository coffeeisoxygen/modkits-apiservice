"""core setup for logging."""

import sys
from typing import Literal

from app.config.cfg_app import EnvironmentEnum
from loguru import logger as loguru_logger

EnvType = Literal["development", "production", "testing"]

FORMAT_DEFAULT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level> | {extra}"


class MLogger:
    def __init__(self, env: EnvType, format: str = FORMAT_DEFAULT):
        self.env = env
        self._format = format
        self._logger = loguru_logger
        self._setup()

    def _setup(self):
        self._logger.remove()

        level = "DEBUG" if self.env == "development" else "INFO"

        self._logger.add(
            sys.stdout,
            level=level,
            format=self._format,  # <<--- ini dia
            enqueue=True,
            backtrace=True,
            diagnose=self.env == "development",
        )

    def get_logger(self):
        return self._logger


def main():  # noqa: D103
    logger = MLogger(env="development").get_logger()
    testbind = logger.bind(env=EnvironmentEnum.DEVELOPMENT.value)
    testbind.info("This is an info message")
    testbind.debug("This is a debug message")
    testbind.error("This is an error message")
    testbind.info(f"Current environment: {EnvironmentEnum.DEVELOPMENT.value}")


if __name__ == "__main__":
    main()
