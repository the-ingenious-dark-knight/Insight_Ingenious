"""Utility functions for error handling."""

from typing import Any


def format_error_message(message: str, **kwargs: Any) -> str:
    """
    Format an error message with the given parameters.

    Args:
        message: The message template
        **kwargs: The parameters to format the message with

    Returns:
        The formatted message
    """
    if not kwargs:
        return message

    return message.format(**kwargs)
