"""
Thread-local context management for structured logging.

This module provides functionality for storing and retrieving
context data in thread-local storage.
"""

import threading
from typing import Any, Dict

# Thread-local storage for context data
_context_data = threading.local()


def get_context_data() -> Dict[str, Any]:
    """Get the current thread's context data dictionary."""
    if not hasattr(_context_data, "data"):
        _context_data.data = {}
    return _context_data.data


def set_context(key: str, value: Any) -> None:
    """
    Set a value in the current thread's context.

    Args:
        key: The context key
        value: The context value
    """
    context = get_context_data()
    context[key] = value


def get_context(key: str, default: Any = None) -> Any:
    """
    Get a value from the current thread's context.

    Args:
        key: The context key
        default: The default value to return if the key is not found

    Returns:
        The context value or default
    """
    context = get_context_data()
    return context.get(key, default)


def clear_context() -> None:
    """Clear the current thread's context data."""
    if hasattr(_context_data, "data"):
        _context_data.data.clear()
