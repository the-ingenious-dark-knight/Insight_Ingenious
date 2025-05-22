"""
Examples of using the centralized error handling and logging system.

This module contains examples of how to use the Ingenious framework's
error handling and logging capabilities in your code.
"""

import logging
from typing import Optional, Dict, Any

from ingenious.common.errors import (
    IngeniousError,
    ValidationError,
    NotFoundError,
    ServiceError,
    ConfigurationError,
    register_error_handler,
)
from ingenious.common.logging import (
    get_logger,
    log_execution_time,
    LoggingContext,
)


# Get a logger for this module
logger = get_logger(__name__)


# Example function with error handling
def process_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process user data with proper error handling.

    Args:
        user_data: The user data to process

    Returns:
        Processed user data

    Raises:
        ValidationError: If the user data is invalid
    """
    # Validate the user data
    validation_errors = {}

    if "name" not in user_data or not user_data["name"].strip():
        validation_errors["name"] = "Name is required"

    if "email" not in user_data or not user_data["email"].strip():
        validation_errors["email"] = "Email is required"

    if validation_errors:
        # Raise a validation error with field-specific messages
        raise ValidationError(
            message="Invalid user data",
            fields=validation_errors
        )

    # Process the user data
    logger.info(f"Processing user data for {user_data['name']}")

    # Return the processed data
    return {
        "id": "123",
        "name": user_data["name"],
        "email": user_data["email"],
        "status": "active",
    }


# Example function with performance logging
@log_execution_time()
def expensive_operation(iterations: int = 1000000) -> int:
    """
    Perform an expensive operation with execution time logging.

    Args:
        iterations: Number of iterations to perform

    Returns:
        Result of the operation
    """
    result = 0
    for i in range(iterations):
        result += i

    return result


# Example function with resource not found error
def get_user_by_id(user_id: str) -> Dict[str, Any]:
    """
    Get a user by ID.

    Args:
        user_id: The ID of the user to get

    Returns:
        The user data

    Raises:
        NotFoundError: If the user is not found
    """
    # Simulate a database lookup
    users = {
        "123": {
            "id": "123",
            "name": "John Doe",
            "email": "john@example.com",
        }
    }

    if user_id not in users:
        # Raise a not found error
        raise NotFoundError(
            resource_type="User",
            resource_id=user_id
        )

    return users[user_id]


# Example function with external service error
def call_external_service(service_name: str) -> Dict[str, Any]:
    """
    Call an external service.

    Args:
        service_name: The name of the service to call

    Returns:
        The service response

    Raises:
        ServiceError: If the service call fails
    """
    # Simulate a service call
    if service_name == "payment":
        # Simulate a service error
        raise ServiceError(
            service_name=service_name,
            message="Payment service is currently unavailable"
        )

    return {
        "status": "success",
        "data": {
            "service": service_name,
            "message": "Service call successful",
        }
    }


# Example usage with temporary log level change
def debug_process():
    """Demonstrate using LoggingContext to temporarily change log level."""
    logger.info("This is normal info logging")

    # Temporarily change the log level to DEBUG
    with LoggingContext(logger, level=logging.DEBUG):
        logger.debug("This debug message will be logged")

    # Back to normal log level
    logger.debug("This debug message will NOT be logged")


# Example of custom error handling registration
class CustomError(Exception):
    """Custom exception for demonstration."""
    pass


def handle_custom_error(exc: CustomError) -> Dict[str, Any]:
    """Custom error handler for CustomError."""
    return {
        "error": "CUSTOM_ERROR",
        "message": str(exc),
        "status_code": 418,  # I'm a teapot
    }


# Register the custom error handler
register_error_handler(CustomError, handle_custom_error)


# Example of handling non-Ingenious exceptions
def example_with_standard_exception():
    """Demonstrate handling standard Python exceptions."""
    try:
        # This will raise a standard Python exception
        result = 1 / 0
    except Exception as exc:
        # Convert to an Ingenious error for consistent handling
        raise IngeniousError(
            message="Division by zero error",
            status_code=500,
            error_code="DIVISION_BY_ZERO",
            details={"exception_type": type(exc).__name__}
        ) from exc


# Usage examples
if __name__ == "__main__":
    # Set up logging
    from ingenious.common.logging import setup_logging

    setup_logging(
        app_module_name=__name__,
        log_level="DEBUG",
        log_file="examples.log",
    )

    try:
        # Example with validation error
        process_user_data({})
    except ValidationError as e:
        print(f"Validation error: {e.message}")
        print(f"Error details: {e.details}")

    try:
        # Example with not found error
        get_user_by_id("999")
    except NotFoundError as e:
        print(f"Not found error: {e.message}")

    try:
        # Example with service error
        call_external_service("payment")
    except ServiceError as e:
        print(f"Service error: {e.message}")
        print(f"Service: {e.details['service']}")

    # Example with performance logging
    expensive_operation()

    # Example with context manager
    debug_process()

    # Example with custom error
    try:
        raise CustomError("This is a custom error")
    except CustomError as e:
        error_dict = handle_custom_error(e)
        print(f"Custom error handled: {error_dict}")

    # Example with standard exception conversion
    try:
        example_with_standard_exception()
    except IngeniousError as e:
        print(f"Standard exception converted: {e.message}")
        print(f"Error details: {e.details}")
