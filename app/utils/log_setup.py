"""setup loguru.

1. logger.bind()
Gunakan bind() ketika Anda ingin melampirkan data ekstra yang spesifik untuk satu baris log tertentu. Ini sangat berguna untuk mencatat detail yang hanya relevan pada momen itu.
"example":
    >>> def kirim_notifikasi_email(user_id):
    ...     logger.bind(user_id=user_id).info(
    ...         "Email notifikasi berhasil dikirim."
    ...     )
2. logger.contextualize()
Gunakan contextualize() ketika Anda ingin menambahkan data ekstra yang konsisten di seluruh blok kode tertentu. Data ini akan dilampirkan ke semua pesan log di dalam blok tersebut secara otomatis. Ini ideal untuk melacak alur eksekusi, seperti sebuah permintaan HTTP atau tugas latar belakang.
"example":
    >>> def proses_data(data):
    ...     logger.info("Memulai proses data.")
    ...     logger.debug(f"Data: {data}")
    ...     # ... kode lainnya
    # Menjalankan fungsi di dalam konteks dengan task_id
    >>> task_id = "task-alpha"
    ... with logger.contextualize(task_id=task_id):
        ... logger.info("Memulai alur pekerjaan.")
        ... proses_data([1, 2, 3])
        ... logger.info("Alur pekerjaan selesai.")
    # Output:
    # ... Memulai alur pekerjaan. {'task_id': 'task-alpha'}
    # ... Memulai proses data. {'task_id': 'task-alpha'}
    # ... Data: [1, 2, 3] {'task_id': 'task-alpha'}
    # ... Alur pekerjaan selesai. {'task_id': 'task-alpha'}
3.@logger.catch()
Gunakan @logger.catch atau with logger.catch() untuk menangani dan mencatat pengecualian (exceptions) secara otomatis tanpa perlu blok try...except manual. Ini membuat kode Anda lebih bersih dan memastikan kesalahan tidak terlewatkan.

Kapan Menggunakannya:

Melindungi fungsi atau blok kode yang rentan terhadap kesalahan (misalnya, pembagian dengan nol, akses data yang tidak ada).

Memastikan program tidak berhenti total karena kesalahan yang tidak tertangani.

Saat Anda ingin mencatat jejak kesalahan (traceback)
"example":
    >>> @logger.catch()
    ... def bagi(a, b):
    ...     return a / b
    >>> bagi(10, 0)
    # Output:
    # ... ZeroDivisionError: division by zero
    # ... Traceback (most recent call last):
    # ...   File "script.py", line 1, in <module>
    # ...     bagi(10, 0)
    # ...   File "script.py", line 2, in bagi
    # ...     return a / b
    # ... ZeroDivisionError: division by zero
4. logger_wraps()
Gunakan logger_wraps() untuk mendekorasi fungsi yang ingin Anda lacak masuk dan keluar, serta argumen yang diteruskan. Ini sangat berguna untuk fungsi yang sering dipanggil dan Anda ingin melacak bagaimana mereka digunakan tanpa menambahkan banyak kode logging manual di dalam fungsi itu sendiri.
"example":
    >>> @logger_wraps()
    ... def foo(a, b, c):
    ...     logger.info("Inside the function")
    ...     return a * b * c
    >>> def bar():
    ...     foo(2, 4, c=8)
    >>> bar()
    >>>
    # Output:
    # ... DEBUG: Entering 'foo' (args=(2, 4), kwargs={'c': 8})
    # ... INFO: Inside the function
4. timeit()
Gunakan timeit untuk mengukur waktu eksekusi fungsi. Ini berguna untuk mengidentifikasi bottleneck performa dalam kode Anda.
"example":
    >>> @timeit
    ... def slow_function(x):
    ...     time.sleep(x)
    ...     return x
    >>> slow_function(1)
    # Log: Function 'slow_function' executed in 1.000000 s
"""

# type: ignore
# ruff: noqa
import functools
import logging
import os
import sys
import time
import traceback
import warnings
from collections.abc import Callable
from itertools import takewhile
from typing import Any

import stackprinter
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


def exception_format(record: Any) -> str:
    """Custom format for exceptions using stackprinter."""
    format_ = "{time} {message}\n"
    if record["exception"] is not None:
        record["extra"]["stack"] = stackprinter.format(record["exception"])
        format_ += "{extra[stack]}\n"
    return format_


def add_traceback(record: Any):
    """Add current stacktrace to log record if 'with_traceback' is set in extra."""
    extra = record["extra"]
    if extra.get("with_traceback", False):
        extra["traceback"] = "\n" + "".join(traceback.format_stack())
    else:
        extra["traceback"] = ""


def tracing_formatter(record: Any) -> str:
    """Custom formatter to prefix message with full call stack."""
    frames = takewhile(
        lambda f: "/loguru/" not in f.filename, traceback.extract_stack()
    )
    stack = " > ".join(f"{f.filename}:{f.name}:{f.lineno}" for f in frames)
    record["extra"]["stack"] = stack
    return f"{record['level'].name} | {record['extra']['stack']} - {record['message']}\n{record['exception'] or ''}"


def patch_logger_with_traceback():
    """Patch the global logger to allow displaying stacktrace in log messages.

    Usage:
        patch_logger_with_traceback()
        logger.info("No traceback")
        logger.bind(with_traceback=True).info("With traceback")
    """
    global logger
    logger = logger.patch(add_traceback)
    logger.remove()
    logger.add(
        sys.stderr,
        format="{time} - {message}{extra[traceback]}",
        backtrace=True,
        diagnose=True,
    )


def setup_loguru():
    """Setup loguru logger."""
    logger.remove()  # Remove the default logger
    logger.add(
        sink=sys.stdout,  # Log to stdout # type: ignore
        rotation="1 MB",  # Rotate logs when they reach 1 MB
        retention="7 days",  # Keep logs for 7 days
        level="DEBUG",  # Set the logging level to DEBUG
        format="<green>{time}</green> | <level>{level}</level> | <level>{message}</level> | <cyan>{extra}</cyan>",
        backtrace=True,  # Enable backtrace for exceptions
        diagnose=True,  # Enable diagnostic information for exceptions
        opener=opener,
    )
    # Tambahkan handler khusus untuk exception (ERROR ke atas)
    logger.add(
        sys.stderr,
        level="ERROR",
        format=exception_format,
        backtrace=True,
        diagnose=True,
    )

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


def opener(file: str, flags: int) -> int:
    """Open a file with the given flags.

    This function is used to customize the file opening behavior for loguru.
    To set desired permissions on created log files, use the opener argument to pass in a custom opener with permissions octal:

    Args:
        file (str): The path to the file to open.
        flags (int): The flags to use when opening the file.

    Returns:
        int: The file descriptor for the opened file.
    """
    return os.open(file, flags, 0o600)  # read/write by owner only


class StreamToLogger:
    """Redirects stdout/stderr to loguru logger.

    Usage:
        stream = StreamToLogger(level="INFO")
        with contextlib.redirect_stdout(stream):
            print("This will be logged by loguru.")
    """

    def __init__(self, level: str = "INFO"):
        self._level = level

    def write(self, buffer: str):
        for line in buffer.rstrip().splitlines():
            logger.opt(depth=1).log(self._level, line.rstrip())

    def flush(self):
        pass


def patch_warnings_to_loguru():
    """Redirects Python warnings to loguru logger.

    Usage:
        patch_warnings_to_loguru()
        warnings.warn("This will be logged by loguru.")
    """
    showwarning_ = warnings.showwarning

    def showwarning(message, *args, **kwargs):
        logger.opt(depth=2).warning(message)
        showwarning_(message, *args, **kwargs)

    warnings.showwarning = showwarning
