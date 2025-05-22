"""
Examples of using the enhanced error handling and logging features.

This module demonstrates how to use the new error types, structured logging,
error conversion utilities, and testing helpers in your code.
"""

import logging
from typing import Dict, Any, Optional

# Import base error and logging classes
from ingenious.common.errors import (
    IngeniousError,
    ValidationError,
    NotFoundError,
    ServiceError,
)

# Import specialized error types
from ingenious.common.errors.database_errors import (
    DatabaseError,
    QueryError,
    DataIntegrityError,
)
from ingenious.common.errors.cache_errors import (
    CacheError,
    CacheConnectionError,
)
from ingenious.common.errors.rate_limit_errors import (
    RateLimitError,
    QuotaExceededError,
)

# Import error conversion utilities
from ingenious.common.errors.converters import (
    convert_exception,
    register_exception_converter,
)

# Import enhanced logging features
from ingenious.common.logging.structured import (
    get_structured_logger,
    with_correlation_id,
    setup_json_logging,
)

# Import testing utilities
from ingenious.common.errors.testing import (
    assert_raises,
    assert_ingenious_error,
    MockException,
    assert_error_conversion,
)


# Get a structured logger
logger = get_structured_logger(
    __name__,
    mask_fields=["password", "token", "api_key"]
)


# Example function with database error handling
def query_database(query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Execute a database query with error handling.

    Args:
        query: SQL query to execute
        params: Query parameters

    Returns:
        Query results

    Raises:
        QueryError: If the query fails
        DataIntegrityError: If the data violates constraints
    """
    try:
        # Simulate a database query
        if "syntax error" in query.lower():
            raise Exception("SQL syntax error")

        if "duplicate key" in query.lower():
            raise Exception("Duplicate key value violates unique constraint")

        # Successful query
        logger.info("Database query executed", extra={"query": query})
        return {"results": ["row1", "row2"]}

    except Exception as exc:
        # Convert the exception to an Ingenious error
        ingenious_error = convert_exception(exc)

        # Re-raise the converted error
        raise ingenious_error


# Example function with cache error handling
def get_cached_value(key: str) -> Any:
    """
    Get a value from the cache with error handling.

    Args:
        key: Cache key

    Returns:
        Cached value

    Raises:
        CacheConnectionError: If the cache connection fails
        CacheKeyError: If the key operation fails
    """
    try:
        # Simulate a cache get
        if key == "connection_error":
            raise Exception("Cache connection failed")

        if key == "invalid_key":
            raise Exception("Invalid key format")

        # Successful cache get
        logger.info("Cache hit", extra={"key": key})
        return {"value": "cached_data"}

    except Exception as exc:
        # For demonstration, manually convert to specific error types
        if "connection" in str(exc).lower():
            raise CacheConnectionError(
                message=str(exc),
                cache_name="redis",
                operation="get"
            )

        if "key" in str(exc).lower():
            raise CacheKeyError(
                message=str(exc),
                key=key
            )

        # Generic cache error
        raise CacheError(message=str(exc))


# Example function with rate limit error handling
def make_api_request(endpoint: str, user_id: str) -> Dict[str, Any]:
    """
    Make an API request with rate limit handling.

    Args:
        endpoint: API endpoint
        user_id: User ID

    Returns:
        API response

    Raises:
        RateLimitError: If the rate limit is exceeded
        QuotaExceededError: If the quota is exceeded
        ServiceError: If the service fails
    """
    try:
        # Simulate rate limiting
        if user_id == "rate_limited":
            raise Exception("Rate limit exceeded")

        if user_id == "quota_exceeded":
            raise Exception("Monthly quota exceeded")

        # Successful API request
        logger.info(
            "API request successful",
            extra={
                "endpoint": endpoint,
                "user_id": user_id
            }
        )
        return {"data": "api_response"}

    except Exception as exc:
        # For demonstration, manually convert to specific error types
        if "rate limit" in str(exc).lower():
            raise RateLimitError(
                message=str(exc),
                limit=100,
                reset_after=60,
                scope="user"
            )

        if "quota" in str(exc).lower():
            raise QuotaExceededError(
                message=str(exc),
                quota=10000,
                usage=10001,
                resource="api_calls",
                reset_time="2023-12-01T00:00:00Z"
            )

        # Generic service error
        raise ServiceError(
            service_name="api",
            message=str(exc)
        )


# Example function with decorator for correlation ID tracking
@with_correlation_id()
def process_user_request(user_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a user request with correlation ID tracking.

    Args:
        user_id: User ID
        request_data: Request data

    Returns:
        Response data
    """
    # Log with the correlation ID
    logger.info(
        f"Processing request for user {user_id}",
        extra={"request_data": request_data}
    )

    # Make a database query
    try:
        query_database("SELECT * FROM users WHERE id = :id", {"id": user_id})
    except DatabaseError as exc:
        logger.error(f"Database error: {exc.message}", extra={"error_code": exc.error_code})

    # Get cached data
    try:
        get_cached_value(f"user:{user_id}")
    except CacheError as exc:
        logger.error(f"Cache error: {exc.message}")

    # Make an API request
    try:
        make_api_request("/users/profile", user_id)
    except RateLimitError as exc:
        logger.warning(
            f"Rate limit error: {exc.message}",
            extra={"reset_after": exc.details.get("reset_after")}
        )

    # Return response
    return {"status": "success"}


# Example function with sensitive data masking
def authenticate_user(username: str, password: str, api_key: str) -> Dict[str, Any]:
    """
    Authenticate a user with sensitive data masking.

    Args:
        username: Username
        password: Password
        api_key: API key

    Returns:
        Authentication result
    """
    # Log with sensitive data that will be masked
    logger.info(
        f"Authenticating user {username}",
        extra={
            "username": username,
            "password": password,  # This will be masked
            "api_key": api_key,    # This will be masked
        }
    )

    # Return authentication result
    return {"authenticated": True, "token": "secret_token"}


# Example of testing error handling
def demonstrate_testing_utilities():
    """Demonstrate how to use the testing utilities."""
    # Using assert_raises
    try:
        with assert_raises(ValidationError, message="Validation failed"):
            raise ValidationError(message="Validation failed")
        print("assert_raises test passed")
    except AssertionError:
        print("assert_raises test failed")

    # Using assert_ingenious_error decorator
    @assert_ingenious_error(NotFoundError, message="User not found")
    def test_function():
        raise NotFoundError(
            resource_type="User",
            resource_id="123",
            message="User not found"
        )

    try:
        test_function()
        print("This line should not be reached")
    except NotFoundError:
        print("assert_ingenious_error test passed")

    # Using MockException
    try:
        with MockException(ValueError, message="Invalid value"):
            pass  # This will raise the mock exception
    except ValueError as exc:
        print(f"MockException test passed: {exc}")

    # Using assert_error_conversion
    original_exception = ValueError("Invalid value")
    try:
        assert_error_conversion(
            original_exception,
            ValidationError,
            {"status_code": 400}
        )
        print("assert_error_conversion test passed")
    except AssertionError as exc:
        print(f"assert_error_conversion test failed: {exc}")


# Main example execution
if __name__ == "__main__":
    # Set up JSON-formatted logging
    setup_json_logging(
        app_module_name=__name__,
        log_level="DEBUG",
        log_file="enhanced_examples.log",
    )

    # Demonstrate structured logging with correlation ID
    process_user_request("user123", {"action": "get_profile"})

    # Demonstrate sensitive data masking
    authenticate_user("john_doe", "secret_password", "api_key_123456")

    # Demonstrate database error handling
    try:
        query_database("SELECT * FROM users WHERE syntax error")
    except QueryError as exc:
        print(f"Database query error: {exc.message}")

    # Demonstrate cache error handling
    try:
        get_cached_value("connection_error")
    except CacheConnectionError as exc:
        print(f"Cache connection error: {exc.message}")

    # Demonstrate rate limit error handling
    try:
        make_api_request("/users/profile", "rate_limited")
    except RateLimitError as exc:
        print(f"Rate limit error: {exc.message}")
        print(f"Reset after: {exc.details.get('reset_after')} seconds")

    # Demonstrate testing utilities
    demonstrate_testing_utilities()
