"""setup loguru."""

import functools
import logging
import sys
import time
from collections.abc import Callable
from typing import Any

from loguru import logger


def logger_wraps(
    *, entry: bool = True, exit: bool = True, level: str = "DEBUG"
) -> Callable:
    """Decorator to log entry and exit of a function.

    Args:
        entry (bool): Log when entering the function.
        exit (bool): Log when exiting the function.
        level (str): Logging level to use.

    Returns:
        Callable: Decorator for logging.

    Example:
        >>> @logger_wraps()
        ... def foo(a, b, c):
        ...     logger.info("Inside the function")
        ...     return a * b * c
        >>> def bar():
        ...     foo(2, 4, c=8)
        >>> bar()
    """

    def wrapper(func: Any):
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            if entry:
                logger_.log(
                    level, "Entering '{}' (args={}, kwargs={})", name, args, kwargs
                )
            result = func(*args, **kwargs)
            if exit:
                logger_.log(level, "Exiting '{}' (result={})", name, result)
            return result

        return wrapped

    return wrapper


def timeit(func: Callable) -> Callable:
    """Decorator to measure execution time of a function.

    Example:
        >>> @timeit
        ... def slow_function(x):
        ...     time.sleep(x)
        ...     return x
        >>> slow_function(1)
        # Log: Function 'slow_function' executed in 1.000000 s

    Args:
        func (Callable): The function to be decorated.

    Returns:
        Callable: The wrapped function with timing.
    """

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug("Function '{}' executed in {:f} s", func.__name__, end - start)
        return result

    return wrapped


def setup_loguru():
    """Setup loguru logger."""
    logger.remove()  # Remove the default logger
    logger.add(
        sink=sys.stdout,  # Log to stdout # type: ignore
        rotation="1 MB",  # Rotate logs when they reach 1 MB
        retention="7 days",  # Keep logs for 7 days
        level="DEBUG",  # Set the logging level to DEBUG
        format="<green>{time}</green> | <level>{level}</level> | <level>{message}</level> | <cyan>{extra}</cyan>",
    )  # Pada logger.add, sink=sys.stdout sudah benar untuk output ke terminal.

    # Intercept standard logging messages and send them to loguru
    class InterceptHandler(logging.Handler):
        """Intercepts standard logging messages and sends them to loguru."""

        def emit(self, record: Any):
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno
            logger.opt(depth=6, exception=record.exc_info).log(
                level, record.getMessage()
            )

    # Remove existing handlers and add the intercept handler
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
