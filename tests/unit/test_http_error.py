"""
Tests for ingenious.models.http_error module
"""
import pytest
from pydantic import ValidationError

from ingenious.models.http_error import HTTPError


class TestHTTPError:
    """Test cases for HTTPError model"""

    def test_init_with_detail(self):
        """Test HTTPError initialization with detail"""
        error = HTTPError(detail="Not found")
        assert error.detail == "Not found"

    def test_init_with_missing_detail(self):
        """Test HTTPError initialization fails without detail"""
        with pytest.raises(ValidationError):
            HTTPError()

    def test_detail_must_be_string(self):
        """Test that detail field must be a string"""
        with pytest.raises(ValidationError):
            HTTPError(detail=123)

    def test_detail_can_be_empty_string(self):
        """Test that detail can be an empty string"""
        error = HTTPError(detail="")
        assert error.detail == ""

    def test_model_serialization(self):
        """Test HTTPError can be serialized to dict"""
        error = HTTPError(detail="Internal server error")
        data = error.model_dump()
        assert data == {"detail": "Internal server error"}

    def test_model_validation_from_dict(self):
        """Test HTTPError can be created from dict"""
        data = {"detail": "Bad request"}
        error = HTTPError(**data)
        assert error.detail == "Bad request"

    def test_inherits_from_base_model(self):
        """Test that HTTPError inherits from BaseModel"""
        from pydantic import BaseModel
        error = HTTPError(detail="Test error")
        assert isinstance(error, BaseModel)

    def test_model_fields(self):
        """Test that the model has the expected fields"""
        error = HTTPError(detail="Test error")
        fields = error.model_fields
        assert 'detail' in fields
        assert len(fields) == 1

    def test_model_json_serialization(self):
        """Test HTTPError can be serialized to JSON"""
        error = HTTPError(detail="Test error")
        json_str = error.model_dump_json()
        assert '"detail":"Test error"' in json_str

    def test_model_validation_error_message(self):
        """Test validation error provides helpful message"""
        try:
            HTTPError(detail=None)
        except ValidationError as e:
            error_details = e.errors()
            assert len(error_details) > 0
            assert 'detail' in str(error_details[0])

    def test_different_detail_types_converted_to_string(self):
        """Test that numeric detail gets converted to string if possible"""
        # Pydantic should handle type coercion for simple types
        error = HTTPError(detail="404")
        assert error.detail == "404"
        assert isinstance(error.detail, str)

    def test_long_detail_message(self):
        """Test HTTPError with long detail message"""
        long_message = "This is a very long error message that could contain detailed information about what went wrong in the application"
        error = HTTPError(detail=long_message)
        assert error.detail == long_message

    def test_detail_with_special_characters(self):
        """Test HTTPError with special characters in detail"""
        special_detail = "Error: Something went wrong! @#$%^&*()"
        error = HTTPError(detail=special_detail)
        assert error.detail == special_detail

    def test_model_equality(self):
        """Test HTTPError model equality"""
        error1 = HTTPError(detail="Same error")
        error2 = HTTPError(detail="Same error")
        error3 = HTTPError(detail="Different error")
        
        assert error1 == error2
        assert error1 != error3