"""
Tests for the error handling utilities in ingenious.common.errors.testing.
"""

import pytest

from ingenious.common.errors.base import IngeniousError
from ingenious.common.errors.common import NotFoundError, ValidationError
from ingenious.common.errors.testing import (
    MockException,
    assert_error_conversion,
    assert_ingenious_error,
    assert_raises,
)


class TestErrorUtilities:
    """Test suite for error utilities."""

    def test_assert_raises_success(self):
        """Test assert_raises works when the expected exception is raised."""
        with assert_raises(ValueError):
            raise ValueError("Test exception")

    def test_assert_raises_with_message(self):
        """Test assert_raises works with message matching."""
        with assert_raises(ValueError, message="Test message"):
            raise ValueError("Test message")

    def test_assert_raises_with_attributes(self):
        """Test assert_raises works with attribute checking."""
        class CustomError(Exception):
            def __init__(self, message, code):
                super().__init__(message)
                self.code = code
                self.info = "additional info"

        with assert_raises(CustomError, code=404, info="additional info"):
            raise CustomError("Not found", 404)

    def test_assert_raises_failure_wrong_exception(self):
        """Test assert_raises fails when the wrong exception is raised."""
        with pytest.raises(TypeError):
            with assert_raises(ValueError):
                raise TypeError("Wrong exception")

    def test_assert_raises_failure_wrong_message(self):
        """Test assert_raises fails when the message doesn't match."""
        with pytest.raises(AssertionError):
            with assert_raises(ValueError, message="Expected message"):
                raise ValueError("Actual message")

    def test_assert_raises_failure_wrong_attribute(self):
        """Test assert_raises fails when an attribute doesn't match."""
        class CustomError(Exception):
            def __init__(self, code):
                self.code = code

        with pytest.raises(AssertionError):
            with assert_raises(CustomError, code=404):
                raise CustomError(500)

    def test_assert_raises_failure_missing_attribute(self):
        """Test assert_raises fails when an expected attribute is missing."""
        with pytest.raises(AssertionError):
            with assert_raises(ValueError, missing_attr=True):
                raise ValueError("Test")

    def test_assert_ingenious_error_decorator(self):
        """Test assert_ingenious_error decorator works."""
        @assert_ingenious_error(NotFoundError, message="Resource not found")
        def function_that_raises():
            raise NotFoundError("Resource not found")

        function_that_raises()

    def test_assert_ingenious_error_decorator_failure(self):
        """Test assert_ingenious_error decorator fails appropriately."""
        @assert_ingenious_error(NotFoundError, message="Resource not found")
        def function_that_raises_wrong_error():
            raise ValidationError("Invalid data")

        with pytest.raises(AssertionError):
            function_that_raises_wrong_error()

    def test_mock_exception(self):
        """Test MockException creates exceptions with custom attributes."""
        with pytest.raises(ValueError) as exc_info:
            with MockException(ValueError, message="Test message", code=404):
                pass

        assert str(exc_info.value) == "Test message"
        assert exc_info.value.code == 404

    def test_assert_error_conversion(self):
        """Test assert_error_conversion validates error conversion."""
        # Create a custom conversion function to test
        class ExternalApiError(Exception):
            def __init__(self, message, status_code):
                super().__init__(message)
                self.status_code = status_code

        class ApiError(IngeniousError):
            """API error that includes the status code."""
            def __init__(self, message, status_code):
                super().__init__(message)
                self.status_code = status_code

        from ingenious.common.errors.converters import register_converter

        # Register a converter for ExternalApiError to ApiError
        @register_converter(ExternalApiError)
        def convert_external_api_error(exc):
            return ApiError(str(exc), exc.status_code)

        # Test the conversion
        original_exception = ExternalApiError("API rate limit exceeded", 429)
        assert_error_conversion(
            original_exception,
            ApiError,
            {"status_code": 429}
        )
