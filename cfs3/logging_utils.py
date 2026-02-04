import logging
import sys
import os
import time
from functools import wraps
from contextlib import contextmanager
from typing import Optional

def get_logger(name: Optional[str] = None, level: int = logging.DEBUG) -> logging.Logger:
    """
    Return a consistent logger instance.

    - Defaults to DEBUG level.
    - Adds a StreamHandler if no handlers exist on this logger and not running under pytest.
    - Under pytest, logs are captured by pytest; no handlers are added or removed.
    - Always propagates so higher-level frameworks can capture messages.
    """
    logger = logging.getLogger(name or "cfs3")
    logger.setLevel(level)

    # Detect pytest environment
    under_pytest = "PYTEST_CURRENT_TEST" in os.environ

    # Only attach a handler if no handlers exist on this logger and not running under pytest
    if not under_pytest and len(logger.handlers) == 0:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Always propagate to allow pytest or parent loggers to capture messages
    logger.propagate = True

    return logger


# Global flag to enable/disable timing
_TIMING_ENABLED = False


def enable_timing():
    """Enable timing output globally."""
    global _TIMING_ENABLED
    _TIMING_ENABLED = True


def disable_timing():
    """Disable timing output globally."""
    global _TIMING_ENABLED
    _TIMING_ENABLED = False


def is_timing_enabled():
    """Check if timing is currently enabled."""
    return _TIMING_ENABLED


def timed(func=None, *, name=None, output_func=None, threshold=None, enabled=None):
    """
    Decorator to time function execution.
    
    Args:
        func: The function to decorate (automatically provided when used as @timed)
        name: Optional custom name for the timed operation (defaults to function name)
        output_func: Optional function to call with timing message (defaults to print)
        threshold: Optional minimum time in seconds to report (only report if exceeds threshold)
        enabled: Optional boolean to enable/disable timing (overrides global flag)
    
    Usage:
        @timed
        def my_function():
            ...
        
        @timed(name="Custom Operation")
        def my_function():
            ...
        
        @timed(threshold=0.1)  # Only report if takes > 0.1 seconds
        def my_function():
            ...
        
        @timed(enabled=True)  # Force timing regardless of global flag
        def my_function():
            ...
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Check if timing is enabled: use explicit enabled param, otherwise global flag
            is_enabled = enabled if enabled is not None else _TIMING_ENABLED
            if not is_enabled:
                return f(*args, **kwargs)
            
            operation_name = name or f"{f.__module__}.{f.__name__}"
            start_time = time.perf_counter()
            try:
                result = f(*args, **kwargs)
                return result
            finally:
                elapsed = time.perf_counter() - start_time
                if threshold is None or elapsed >= threshold:
                    message = f"[TIMING] {operation_name}: {elapsed:.4f}s"
                    if output_func:
                        output_func(message)
                    else:
                        print(message)
        return wrapper
    
    # Handle both @timed and @timed(...) syntax
    if func is None:
        return decorator
    else:
        return decorator(func)


@contextmanager
def timing(name, output_func=None, threshold=None, enabled=None):
    """
    Context manager to time a code block.
    
    Args:
        name: Name of the operation being timed
        output_func: Optional function to call with timing message (defaults to print)
        threshold: Optional minimum time in seconds to report
        enabled: Optional boolean to enable/disable timing (overrides global flag)
    
    Usage:
        with timing("load data"):
            data = load_large_file()
        
        with timing("process", output_func=logger.info):
            process_data()
        
        with timing("quick operation", threshold=0.1):
            # Only reported if takes > 0.1 seconds
            do_something()
        
        with timing("important op", enabled=True):
            # Force timing regardless of global flag
            do_critical_work()
    """
    # Check if timing is enabled: use explicit enabled param, otherwise global flag
    is_enabled = enabled if enabled is not None else _TIMING_ENABLED
    if not is_enabled:
        yield
        return
    
    start_time = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start_time
        if threshold is None or elapsed >= threshold:
            message = f"[TIMING] {name}: {elapsed:.4f}s"
            if output_func:
                output_func(message)
            else:
                print(message)
