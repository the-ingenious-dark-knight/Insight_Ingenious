"""
Tests for ingenious.models.functional_tests module
"""

import pytest
from pydantic import ValidationError

from ingenious.models.functional_tests import Event


class TestEvent:
    """Test cases for Event model"""

    def test_init_with_valid_data(self):
        """Test Event initialization with valid data"""
        event = Event(
            file_name="test.txt",
            event_type="create",
            response_content="File created successfully",
            identifier="test-123",
        )
        assert event.file_name == "test.txt"
        assert event.event_type == "create"
        assert event.response_content == "File created successfully"
        assert event.identifier == "test-123"

    def test_init_with_missing_file_name(self):
        """Test Event initialization fails without file_name"""
        with pytest.raises(ValidationError):
            Event(
                event_type="create",
                response_content="File created successfully",
                identifier="test-123",
            )

    def test_init_with_missing_event_type(self):
        """Test Event initialization fails without event_type"""
        with pytest.raises(ValidationError):
            Event(
                file_name="test.txt",
                response_content="File created successfully",
                identifier="test-123",
            )

    def test_init_with_missing_response_content(self):
        """Test Event initialization fails without response_content"""
        with pytest.raises(ValidationError):
            Event(file_name="test.txt", event_type="create", identifier="test-123")

    def test_init_with_missing_identifier(self):
        """Test Event initialization fails without identifier"""
        with pytest.raises(ValidationError):
            Event(
                file_name="test.txt",
                event_type="create",
                response_content="File created successfully",
            )

    def test_all_fields_must_be_strings(self):
        """Test that all fields must be strings"""
        with pytest.raises(ValidationError):
            Event(
                file_name=123,
                event_type="create",
                response_content="File created successfully",
                identifier="test-123",
            )

        with pytest.raises(ValidationError):
            Event(
                file_name="test.txt",
                event_type=123,
                response_content="File created successfully",
                identifier="test-123",
            )

        with pytest.raises(ValidationError):
            Event(
                file_name="test.txt",
                event_type="create",
                response_content=123,
                identifier="test-123",
            )

        with pytest.raises(ValidationError):
            Event(
                file_name="test.txt",
                event_type="create",
                response_content="File created successfully",
                identifier=123,
            )

    def test_model_serialization(self):
        """Test Event can be serialized to dict"""
        event = Event(
            file_name="test.txt",
            event_type="create",
            response_content="File created successfully",
            identifier="test-123",
        )
        data = event.model_dump()
        expected = {
            "file_name": "test.txt",
            "event_type": "create",
            "response_content": "File created successfully",
            "identifier": "test-123",
        }
        assert data == expected

    def test_model_validation_from_dict(self):
        """Test Event can be created from dict"""
        data = {
            "file_name": "test.txt",
            "event_type": "update",
            "response_content": "File updated successfully",
            "identifier": "test-456",
        }
        event = Event(**data)
        assert event.file_name == "test.txt"
        assert event.event_type == "update"
        assert event.response_content == "File updated successfully"
        assert event.identifier == "test-456"

    def test_empty_strings_are_valid(self):
        """Test that empty strings are valid for all fields"""
        event = Event(file_name="", event_type="", response_content="", identifier="")
        assert event.file_name == ""
        assert event.event_type == ""
        assert event.response_content == ""
        assert event.identifier == ""

    def test_different_event_types(self):
        """Test Event with different event types"""
        event_types = ["create", "update", "delete", "read", "custom_event"]

        for event_type in event_types:
            event = Event(
                file_name="test.txt",
                event_type=event_type,
                response_content=f"Event {event_type} processed",
                identifier=f"test-{event_type}",
            )
            assert event.event_type == event_type
