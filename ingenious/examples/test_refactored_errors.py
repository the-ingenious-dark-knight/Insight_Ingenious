"""
Test the refactored error module.

This script verifies that the error module refactoring works correctly
by testing imports and error class functionality.
"""

import traceback

print("Importing error classes...")
try:
    from ingenious.common.errors import (
        IngeniousError,
        ValidationError,
        NotFoundError,
        AuthenticationError,
        AuthorizationError,
        ServiceError,
        ConfigurationError,
        ContentFilterError,
        TokenLimitExceededError,
        handle_exception,
    )
    print("Successfully imported base error classes")

    # Try importing specialized errors
    try:
        from ingenious.common.errors import (
            CacheError,
            DatabaseError,
            RateLimitError,
        )
        print("Successfully imported specialized error classes")
    except ImportError as e:
        print(f"Error importing specialized classes: {e}")
        traceback.print_exc()

    # Test creating a basic error
    basic_error = IngeniousError("Test error")
    print(f"Basic error: {basic_error}")
    print(f"To dictionary: {basic_error.to_dict()}")

    # Test creating a validation error
    validation_error = ValidationError("Invalid input", fields={"name": "Required field"})
    print(f"\nValidation error: {validation_error}")
    print(f"To dictionary: {validation_error.to_dict()}")

    # Test creating a not found error
    not_found_error = NotFoundError("User", "123")
    print(f"\nNot found error: {not_found_error}")
    print(f"To dictionary: {not_found_error.to_dict()}")

    # Test creating a specialized error
    token_limit_error = TokenLimitExceededError(max_context_length=4096, requested_tokens=4500)
    print(f"\nToken limit error: {token_limit_error}")
    print(f"To dictionary: {token_limit_error.to_dict()}")

    # Test error handlers
    try:
        raise ValueError("Test value error")
    except Exception as e:
        result = handle_exception(e)
        print(f"\nHandled exception: {result}")

    print("\nAll tests passed!")

except Exception as e:
    print(f"Error in test: {e}")
    traceback.print_exc()
