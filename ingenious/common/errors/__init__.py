"""
Centralized error handling for the Ingenious framework.

This module provides base exception classes and error utilities to standardize
error handling across the application.
"""

import logging
import traceback
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union

# Import specialized error types
from ingenious.common.errors.content_filter_error import ContentFilterError
from ingenious.common.errors.token_limit_exceeded_error import TokenLimitExceededError

# Try to import the new error modules if they exist
try:
    from ingenious.common.errors.database_errors import (
        ConnectionError as DBConnectionError,  # Renamed to avoid conflict
    )
    from ingenious.common.errors.database_errors import (
        DatabaseError,
        DataIntegrityError,
        QueryError,
        TransactionError,
    )
except ImportError:
    pass  # Module not yet available

try:
    from ingenious.common.errors.cache_errors import (
        CacheConnectionError,
        CacheError,
        CacheKeyError,
    )
except ImportError:
    pass  # Module not yet available

try:
    from ingenious.common.errors.rate_limit_errors import (
        QuotaExceededError,
        RateLimitError,
    )
except ImportError:
    pass  # Module not yet available


# Create a logger for the errors module
logger = logging.getLogger(__name__)

# Type variable for error handlers
T = TypeVar("T")


class IngeniousError(Exception):
    """Base exception class for all Ingenious application errors."""

    def __init__(
        self,
        message: str = "An error occurred in the Ingenious application",
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the base Ingenious error.

        Args:
            message: Human-readable error message
            status_code: HTTP status code to return if this is an API error
            error_code: Machine-readable error code
            details: Additional error details and context
        """
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary representation."""
        error_dict = {
            "error": self.error_code,
            "message": self.message,
            "status_code": self.status_code,
        }

        if self.details:
            error_dict["details"] = self.details

        return error_dict

    def log(
        self, log_level: int = logging.ERROR, include_traceback: bool = True
    ) -> None:
        """
        Log the error with appropriate severity.

        Args:
            log_level: The logging level to use
            include_traceback: Whether to include the traceback in the log
        """
        error_dict = self.to_dict()
        log_message = f"Error {self.error_code}: {self.message}"

        if include_traceback:
            log_message += f"\nDetails: {error_dict}"
            logger.log(log_level, log_message, exc_info=True)
        else:
            logger.log(log_level, log_message)


class ValidationError(IngeniousError):
    """Error raised when validation fails."""

    def __init__(
        self,
        message: str = "Validation error",
        fields: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        """
        Initialize the validation error.

        Args:
            message: Human-readable error message
            fields: Dictionary of field-specific validation errors
            **kwargs: Additional arguments to pass to the parent class
        """
        details = {"fields": fields or {}}
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details,
            **kwargs,
        )


class NotFoundError(IngeniousError):
    """Error raised when a requested resource is not found."""

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        message: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the not found error.

        Args:
            resource_type: Type of resource that was not found
            resource_id: ID of the resource that was not found
            message: Optional custom error message
            **kwargs: Additional arguments to pass to the parent class
        """
        if message is None:
            message = f"{resource_type} with ID '{resource_id}' not found"

        details = {"resource_type": resource_type, "resource_id": resource_id}
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details=details,
            **kwargs,
        )


class AuthenticationError(IngeniousError):
    """Error raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed", **kwargs):
        """
        Initialize the authentication error.

        Args:
            message: Human-readable error message
            **kwargs: Additional arguments to pass to the parent class
        """
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            **kwargs,
        )


class AuthorizationError(IngeniousError):
    """Error raised when authorization fails."""

    def __init__(
        self, message: str = "Not authorized to perform this action", **kwargs
    ):
        """
        Initialize the authorization error.

        Args:
            message: Human-readable error message
            **kwargs: Additional arguments to pass to the parent class
        """
        super().__init__(
            message=message, status_code=403, error_code="AUTHORIZATION_ERROR", **kwargs
        )


class ServiceError(IngeniousError):
    """Error raised when an external service fails."""

    def __init__(
        self, service_name: str, message: str = "External service error", **kwargs
    ):
        """
        Initialize the service error.

        Args:
            service_name: Name of the external service that failed
            message: Human-readable error message
            **kwargs: Additional arguments to pass to the parent class
        """
        details = {"service": service_name}
        super().__init__(
            message=message,
            status_code=502,
            error_code="SERVICE_ERROR",
            details=details,
            **kwargs,
        )


class ConfigurationError(IngeniousError):
    """Error raised when there's a configuration issue."""

    def __init__(
        self,
        message: str = "Configuration error",
        config_key: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the configuration error.

        Args:
            message: Human-readable error message
            config_key: The configuration key that has an issue
            **kwargs: Additional arguments to pass to the parent class
        """
        details = {}
        if config_key:
            details["config_key"] = config_key

        super().__init__(
            message=message,
            status_code=500,
            error_code="CONFIGURATION_ERROR",
            details=details,
            **kwargs,
        )


# Registry for error handlers
_error_handlers: Dict[Type[Exception], Callable] = {}


def register_error_handler(
    exception_class: Type[Exception], handler: Callable[[Exception], T]
) -> None:
    """
    Register an error handler for a specific exception type.

    Args:
        exception_class: The exception class to handle
        handler: The handler function
    """
    _error_handlers[exception_class] = handler


def get_error_handler(exception_class: Type[Exception]) -> Optional[Callable]:
    """
    Get an error handler for an exception class.

    This will search for handlers registered for the exception class
    and its parent classes.

    Args:
        exception_class: The exception class to find a handler for

    Returns:
        The handler function or None if no handler is found
    """
    # Try to find an exact match
    if exception_class in _error_handlers:
        return _error_handlers[exception_class]

    # Try to find a parent class handler
    for handler_class in _error_handlers:
        if issubclass(exception_class, handler_class):
            return _error_handlers[handler_class]

    return None


def handle_exception(exc: Exception) -> Any:
    """
    Handle an exception using registered error handlers.

    Args:
        exc: The exception to handle

    Returns:
        The result of the error handler
    """
    handler = get_error_handler(type(exc))

    if handler:
        return handler(exc)

    # Default behavior for unhandled exceptions
    if isinstance(exc, IngeniousError):
        exc.log()
        return exc.to_dict()

    # Log unhandled exceptions
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    # Convert to a generic error
    generic_error = IngeniousError(
        message=str(exc) or "An unexpected error occurred",
        details={"exception_type": exc.__class__.__name__},
    )

    return generic_error.to_dict()
