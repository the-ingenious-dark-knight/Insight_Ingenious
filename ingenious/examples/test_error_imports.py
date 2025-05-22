"""
Test the error module refactoring.

This script tests that all error classes are properly imported and available
through the ingenious.common.errors module.
"""

import sys
import traceback
from pprint import pprint

# Import the errors module
print("Importing ingenious.common.errors...")
try:
    import ingenious.common.errors as errors
    print("Successfully imported ingenious.common.errors")
except Exception as e:
    print(f"Error importing ingenious.common.errors: {e}")
    traceback.print_exc()
    sys.exit(1)

# List all classes defined in the errors module
error_classes = [
    name for name in dir(errors)
    if (isinstance(getattr(errors, name), type) and
        issubclass(getattr(errors, name), errors.IngeniousError) and
        getattr(errors, name) is not errors.IngeniousError)
]

print("\nAvailable error classes:")
pprint(sorted(error_classes))

# Test that we can import specific error classes
print("\nTesting specific imports:")
try:
    from ingenious.common.errors import (
        ContentFilterError, TokenLimitExceededError,
        ValidationError, NotFoundError, ServiceError
    )
    print("✅ Base error classes imported successfully")
except ImportError as e:
    print(f"❌ Failed to import base error classes: {e}")

# Test specialized error classes
try:
    from ingenious.common.errors import (
        CacheError, CacheConnectionError, DatabaseError,
        RateLimitError, QuotaExceededError
    )
    print("✅ Specialized error classes imported successfully")
except ImportError as e:
    print(f"❌ Failed to import specialized error classes: {e}")

# Create and use an error instance
error = errors.ValidationError("Test validation error", fields={"name": "Required field"})
print("\nCreated error instance:")
pprint(error.to_dict())

# List all classes defined in the errors module
error_classes = [
    name for name in dir(errors)
    if (isinstance(getattr(errors, name), type) and
        issubclass(getattr(errors, name), errors.IngeniousError) and
        getattr(errors, name) is not errors.IngeniousError)
]

print("Available error classes:")
pprint(sorted(error_classes))

# Test that we can import specific error classes
print("\nTesting specific imports:")
try:
    from ingenious.common.errors import (
        ContentFilterError, TokenLimitExceededError,
        ValidationError, NotFoundError, ServiceError
    )
    print("✅ Base error classes imported successfully")
except ImportError as e:
    print(f"❌ Failed to import base error classes: {e}")

# Test specialized error classes
try:
    from ingenious.common.errors import (
        CacheError, CacheConnectionError, DatabaseError,
        RateLimitError, QuotaExceededError
    )
    print("✅ Specialized error classes imported successfully")
except ImportError as e:
    print(f"❌ Failed to import specialized error classes: {e}")

# Create and use an error instance
error = errors.ValidationError("Test validation error", fields={"name": "Required field"})
print("\nCreated error instance:")
pprint(error.to_dict())
