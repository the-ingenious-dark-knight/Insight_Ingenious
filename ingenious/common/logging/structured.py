"""
Enhanced logging features for the Ingenious framework.

This module extends the basic logging functionality with structured logging,
request tracking, and sensitive data masking.
"""

import functools
import json
import logging
import threading
import uuid
from typing import Any, Callable, Dict, List, Optional

# Import the base logging module
from ingenious.common.logging import get_logger

# Initialize a logger for this module
logger = get_logger(__name__)


# Thread-local storage for context data
_context_data = threading.local()


def _get_context_data() -> Dict[str, Any]:
    """Get the current thread's context data dictionary."""
    if not hasattr(_context_data, "data"):
        _context_data.data = {}
    return _context_data.data


class StructuredLogger:
    """
    Logger wrapper that supports structured logging and context tracking.

    This class wraps a standard Python logger and adds support for:
    - Structured logging with JSON format
    - Thread-local context data
    - Correlation ID tracking
    - Sensitive data masking
    """

    def __init__(
        self,
        name: str,
        mask_fields: Optional[List[str]] = None,
        level: int = logging.NOTSET,
    ):
        """
        Initialize the structured logger.

        Args:
            name: The name of the logger
            mask_fields: Fields to mask in logs
            level: The initial logging level
        """
        self.logger = logging.getLogger(name)
        self.mask_fields = set(mask_fields or [])

        if level != logging.NOTSET:
            self.logger.setLevel(level)

    def add_mask_field(self, field_name: str) -> None:
        """Add a field to be masked in logs."""
        self.mask_fields.add(field_name)

    def set_context(self, key: str, value: Any) -> None:
        """
        Set a value in the current thread's context.

        Args:
            key: The context key
            value: The context value
        """
        context = _get_context_data()
        context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the current thread's context.

        Args:
            key: The context key
            default: The default value to return if the key is not found

        Returns:
            The context value or default
        """
        context = _get_context_data()
        return context.get(key, default)

    def clear_context(self) -> None:
        """Clear the current thread's context data."""
        if hasattr(_context_data, "data"):
            _context_data.data.clear()

    def with_correlation_id(
        self, correlation_id: Optional[str] = None
    ) -> "StructuredLogger":
        """
        Set a correlation ID in the current thread's context.

        Args:
            correlation_id: The correlation ID to use (generates a new one if None)

        Returns:
            This logger instance for chaining
        """
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())

        self.set_context("correlation_id", correlation_id)
        return self

    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mask sensitive data in the log data.

        Args:
            data: The data to mask

        Returns:
            The masked data
        """
        # Create a copy to avoid modifying the original
        masked_data = {}

        for key, value in data.items():
            if key in self.mask_fields:
                # Mask the value
                if isinstance(value, str):
                    if len(value) > 4:
                        masked_data[key] = (
                            value[:2] + "*" * (len(value) - 4) + value[-2:]
                        )
                    else:
                        masked_data[key] = "****"
                else:
                    masked_data[key] = "****"
            elif isinstance(value, dict):
                # Recursively mask nested dictionaries
                masked_data[key] = self._mask_sensitive_data(value)
            else:
                masked_data[key] = value

        return masked_data

    def _log(
        self,
        level: int,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info=None,
    ) -> None:
        """
        Log a message with context data.

        Args:
            level: The logging level
            message: The log message
            extra: Additional data to include in the log
            exc_info: Exception info to include
        """
        # Get the current context data
        context = _get_context_data()

        # Combine context and extra data
        log_data = {**context}
        if extra:
            log_data.update(extra)

        # Mask sensitive data
        if self.mask_fields:
            log_data = self._mask_sensitive_data(log_data)

        # Log the message with the data
        self.logger.log(
            level, message, extra={"structured": log_data}, exc_info=exc_info
        )

    def debug(
        self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info=None
    ) -> None:
        """Log a debug message."""
        self._log(logging.DEBUG, message, extra, exc_info)

    def info(
        self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info=None
    ) -> None:
        """Log an info message."""
        self._log(logging.INFO, message, extra, exc_info)

    def warning(
        self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info=None
    ) -> None:
        """Log a warning message."""
        self._log(logging.WARNING, message, extra, exc_info)

    def error(
        self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info=None
    ) -> None:
        """Log an error message."""
        self._log(logging.ERROR, message, extra, exc_info)

    def critical(
        self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info=None
    ) -> None:
        """Log a critical message."""
        self._log(logging.CRITICAL, message, extra, exc_info)

    def exception(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log an exception message."""
        self._log(logging.ERROR, message, extra, exc_info=True)


class JsonFormatter(logging.Formatter):
    """
    JSON formatter for log records.

    This formatter outputs log records in JSON format, which is useful
    for log aggregation systems.
    """

    def __init__(self, include_logger_name=True, include_level_name=True):
        """
        Initialize the JSON formatter.

        Args:
            include_logger_name: Whether to include the logger name
            include_level_name: Whether to include the level name
        """
        super().__init__()
        self.include_logger_name = include_logger_name
        self.include_level_name = include_level_name

    def format(self, record):
        """
        Format a log record as JSON.

        Args:
            record: The log record to format

        Returns:
            The formatted log record as a JSON string
        """
        # Start with the basic record attributes
        log_data = {
            "timestamp": self.formatTime(record),
            "message": record.getMessage(),
        }

        # Add optional attributes
        if self.include_logger_name:
            log_data["logger"] = record.name

        if self.include_level_name:
            log_data["level"] = record.levelname

        # Add structured data if available
        if hasattr(record, "structured") and record.structured:
            log_data.update(record.structured)

        # Add exception info if available
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        # Convert to JSON
        return json.dumps(log_data)


def get_structured_logger(
    name: str, mask_fields: Optional[List[str]] = None, level: int = logging.NOTSET
) -> StructuredLogger:
    """
    Get a structured logger with the given name.

    Args:
        name: The name of the logger
        mask_fields: Fields to mask in logs
        level: The initial logging level

    Returns:
        A structured logger instance
    """
    return StructuredLogger(name, mask_fields, level)


def with_correlation_id(correlation_id: Optional[str] = None) -> Callable:
    """
    Decorator to set a correlation ID for the duration of a function call.

    Args:
        correlation_id: The correlation ID to use (generates a new one if None)

    Returns:
        Decorator function
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get the logger name based on the function's module
            logger_name = func.__module__

            # Create a structured logger
            logger = get_structured_logger(logger_name)

            # Set the correlation ID
            if correlation_id is None:
                new_id = str(uuid.uuid4())
            else:
                new_id = correlation_id

            logger.with_correlation_id(new_id)

            try:
                # Call the function
                return func(*args, **kwargs)
            finally:
                # Clear the context when done
                logger.clear_context()

        return wrapper

    return decorator


def setup_json_logging(
    app_module_name: Optional[str] = None,
    log_level: str = None,
    log_file: Optional[str] = None,
    log_dir: Optional[str] = None,
    include_logger_name: bool = True,
    include_level_name: bool = True,
    **kwargs,
) -> None:
    """
    Set up JSON-formatted logging for the application.

    Args:
        app_module_name: The name of the application module
        log_level: The logging level to use
        log_file: The name of the log file to write to
        log_dir: The directory to store log files in
        include_logger_name: Whether to include the logger name in JSON logs
        include_level_name: Whether to include the level name in JSON logs
        **kwargs: Additional arguments to pass to setup_logging
    """
    # Import the base setup function
    from ingenious.common.logging import setup_logging

    # Set up basic logging
    setup_logging(
        app_module_name=app_module_name,
        log_level=log_level,
        log_file=log_file,
        log_dir=log_dir,
        **kwargs,
    )

    # Replace the formatter with our JSON formatter
    formatter = JsonFormatter(
        include_logger_name=include_logger_name, include_level_name=include_level_name
    )

    # Update handlers on the root logger
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.setFormatter(formatter)

    # Update handlers on the app logger if specified
    if app_module_name:
        app_logger = logging.getLogger(app_module_name)
        for handler in app_logger.handlers:
            handler.setFormatter(formatter)
