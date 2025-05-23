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


def set_context(context: dict = None, value: Any = None):
    """
    Set the entire context dictionary or a single key-value pair.

    Args:
        context: The context dictionary or key-value pair
        value: The context value (optional, used only if setting a single key-value pair)
    """
    if context is not None:
        _context_data.data = context
    elif value is not None:
        raise ValueError("Key must be provided when setting a value.")


def get_context(key: str = None, default: Any = None) -> Any:
    """
    Get a value from the current thread's context, or the whole context if no key is provided.

    Args:
        key: The context key
        default: The default value to return if the key is not found

    Returns:
        The context value or default
    """
    context = get_context_data()
    if key is None:
        return context
    return context.get(key, default)


def clear_context() -> None:
    """Clear the current thread's context data."""
    if hasattr(_context_data, "data"):
        _context_data.data.clear()
