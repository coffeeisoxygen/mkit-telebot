"""Decorators for logging function entry and exit using loguru.

This module provides decorators to automatically log when a function
is entered and exited, including arguments and return values, with
options to log the execution time.
"""

# ruff : noqa
import asyncio
import functools
import time

from loguru import logger


def log_entry_exit(*, entry=True, exit=True, level="DEBUG"):
    """Decorator for logging entry and exit only.

    Args:
        entry (bool): Whether to log when entering the function.
        exit (bool): Whether to log when exiting the function.
        level (str): Log level to use.

    Returns:
        Callable: A decorator that wraps the target function.
    """

    def wrapper(func):
        name = func.__name__

        @functools.wraps(func)
        def sync_wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            if entry:
                logger_.log(level, f"Entering '{name}' (args={args}, kwargs={kwargs})")
            result = func(*args, **kwargs)
            if exit:
                logger_.log(level, f"Exiting '{name}' (result={result})")
            return result

        @functools.wraps(func)
        async def async_wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            if entry:
                logger_.log(level, f"Entering '{name}' (args={args}, kwargs={kwargs})")
            result = await func(*args, **kwargs)
            if exit:
                logger_.log(level, f"Exiting '{name}' (result={result})")
            return result

        return async_wrapped if asyncio.iscoroutinefunction(func) else sync_wrapped

    return wrapper


def log_exec_time(*, entry=True, exit=True, level="DEBUG"):
    """Decorator for logging entry, exit, and execution time (sync & async).

    Args:
        entry (bool): Log when entering the function.
        exit (bool): Log when exiting the function.
        level (str): Log level to use.

    Returns:
        Callable: A decorator that wraps the target function.
    """

    def wrapper(func):
        name = func.__name__

        @functools.wraps(func)
        def sync_wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            if entry:
                logger_.log(level, f"Entering '{name}' (args={args}, kwargs={kwargs})")
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            duration = end - start
            logger_.log(level, f"Execution time for '{name}': {duration:.6f}s")
            if exit:
                logger_.log(level, f"Exiting '{name}' (result={result})")
            return result

        @functools.wraps(func)
        async def async_wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            if entry:
                logger_.log(level, f"Entering '{name}' (args={args}, kwargs={kwargs})")
            start = time.perf_counter()
            result = await func(*args, **kwargs)
            end = time.perf_counter()
            duration = end - start
            logger_.log(level, f"Execution time for '{name}': {duration:.6f}s")
            if exit:
                logger_.log(level, f"Exiting '{name}' (result={result})")
            return result

        return async_wrapped if asyncio.iscoroutinefunction(func) else sync_wrapped

    return wrapper


def timeit(func):
    def wrapped(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug("Function '{}' executed in {:f} s", func.__name__, end - start)
        return result

    return wrapped
