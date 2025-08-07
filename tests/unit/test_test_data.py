"""
Tests for ingenious.models.test_data module
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
import yaml

from ingenious.models.test_data import Event, Events


class TestEvent:
    """Test cases for Event model"""

    def test_init_with_required_fields(self):
        """Test Event initialization with required fields"""
        event = Event(
            identifier="test_123",
            event_type="create",
            file_name="test.txt",
            conversation_flow="main_flow",
            response_content="File created successfully",
        )
        assert event.identifier == "test_123"
        assert event.event_type == "create"
        assert event.file_name == "test.txt"
        assert event.conversation_flow == "main_flow"
        assert event.response_content == "File created successfully"
        assert event.identifier_group == "default"  # default value

    def test_init_with_custom_identifier_group(self):
        """Test Event initialization with custom identifier group"""
        event = Event(
            identifier="test_123",
            event_type="create",
            file_name="test.txt",
            conversation_flow="main_flow",
            response_content="File created successfully",
            identifier_group="custom_group",
        )
        assert event.identifier_group == "custom_group"

    def test_init_missing_required_fields(self):
        """Test Event initialization fails without required fields"""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            Event()  # missing all required fields

        with pytest.raises(ValidationError):
            Event(identifier="test")  # missing other required fields

    def test_model_serialization(self):
        """Test Event can be serialized to dict"""
        event = Event(
            identifier="test_123",
            event_type="create",
            file_name="test.txt",
            conversation_flow="main_flow",
            response_content="File created successfully",
            identifier_group="custom_group",
        )
        data = event.model_dump()
        expected = {
            "identifier": "test_123",
            "event_type": "create",
            "file_name": "test.txt",
            "conversation_flow": "main_flow",
            "response_content": "File created successfully",
            "identifier_group": "custom_group",
        }
        assert data == expected

    def test_model_validation_from_dict(self):
        """Test Event can be created from dict"""
        data = {
            "identifier": "test_456",
            "event_type": "update",
            "file_name": "update.txt",
            "conversation_flow": "update_flow",
            "response_content": "File updated successfully",
        }
        event = Event(**data)
        assert event.identifier == "test_456"
        assert event.event_type == "update"
        assert event.identifier_group == "default"


class TestEvents:
    """Test cases for Events model"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_fs = Mock()
        self.events = Events(self.mock_fs)

    def test_init(self):
        """Test Events initialization"""
        fs = Mock()
        events = Events(fs)
        assert events._fs is fs
        assert events._events == []

    def test_add_event(self):
        """Test adding a single event"""
        event = Event(
            identifier="test_1",
            event_type="create",
            file_name="test.txt",
            conversation_flow="main",
            response_content="Created",
        )

        self.events.add_event(event)
        assert len(self.events._events) == 1
        assert self.events._events[0] is event

    def test_add_multiple_events(self):
        """Test adding multiple events"""
        event1 = Event(
            identifier="test_1",
            event_type="create",
            file_name="test1.txt",
            conversation_flow="main",
            response_content="Created 1",
        )
        event2 = Event(
            identifier="test_2",
            event_type="update",
            file_name="test2.txt",
            conversation_flow="main",
            response_content="Updated 2",
        )

        self.events.add_event(event1)
        self.events.add_event(event2)

        assert len(self.events._events) == 2
        assert self.events._events[0] is event1
        assert self.events._events[1] is event2

    def test_get_events_empty(self):
        """Test get_events returns empty list initially"""
        events = self.events.get_events()
        assert events == []

    def test_get_events_with_data(self):
        """Test get_events returns all events"""
        event1 = Event(
            identifier="test_1",
            event_type="create",
            file_name="test1.txt",
            conversation_flow="main",
            response_content="Created 1",
        )
        event2 = Event(
            identifier="test_2",
            event_type="update",
            file_name="test2.txt",
            conversation_flow="main",
            response_content="Updated 2",
        )

        self.events.add_event(event1)
        self.events.add_event(event2)

        events = self.events.get_events()
        assert len(events) == 2
        assert events[0] is event1
        assert events[1] is event2

    def test_get_event_by_identifier_success(self):
        """Test get_event_by_identifier returns correct event"""
        event1 = Event(
            identifier="test_1",
            event_type="create",
            file_name="test1.txt",
            conversation_flow="main",
            response_content="Created 1",
        )
        event2 = Event(
            identifier="test_2",
            event_type="update",
            file_name="test2.txt",
            conversation_flow="main",
            response_content="Updated 2",
        )

        self.events.add_event(event1)
        self.events.add_event(event2)

        found_event = self.events.get_event_by_identifier("test_2")
        assert found_event is event2

    def test_get_event_by_identifier_not_found(self):
        """Test get_event_by_identifier raises error when not found"""
        event = Event(
            identifier="test_1",
            event_type="create",
            file_name="test1.txt",
            conversation_flow="main",
            response_content="Created 1",
        )
        self.events.add_event(event)

        with pytest.raises(
            ValueError, match="Event with identifier nonexistent not found"
        ):
            self.events.get_event_by_identifier("nonexistent")

    def test_get_events_by_identifier_success(self):
        """Test get_events_by_identifier returns all matching events"""
        event1 = Event(
            identifier="test_same",
            event_type="create",
            file_name="test1.txt",
            conversation_flow="main",
            response_content="Created 1",
        )
        event2 = Event(
            identifier="test_same",
            event_type="update",
            file_name="test2.txt",
            conversation_flow="main",
            response_content="Updated 2",
        )
        event3 = Event(
            identifier="test_different",
            event_type="delete",
            file_name="test3.txt",
            conversation_flow="main",
            response_content="Deleted 3",
        )

        self.events.add_event(event1)
        self.events.add_event(event2)
        self.events.add_event(event3)

        found_events = self.events.get_events_by_identifier("test_same")
        assert len(found_events) == 2
        assert event1 in found_events
        assert event2 in found_events
        assert event3 not in found_events

    def test_get_events_by_identifier_empty(self):
        """Test get_events_by_identifier returns empty list when not found"""
        event = Event(
            identifier="test_1",
            event_type="create",
            file_name="test1.txt",
            conversation_flow="main",
            response_content="Created 1",
        )
        self.events.add_event(event)

        found_events = self.events.get_events_by_identifier("nonexistent")
        assert found_events == []

    @pytest.mark.asyncio
    async def test_load_events_from_file_success(self):
        """Test successful loading of events from file"""
        # Mock file system
        self.mock_fs.check_if_file_exists = AsyncMock(return_value=True)
        yaml_content = [
            {
                "identifier": "test_1",
                "event_type": "create",
                "file_name": "test1.txt",
                "conversation_flow": "main",
                "response_content": "Created 1",
            },
            {
                "identifier": "test_2",
                "event_type": "update",
                "file_name": "test2.txt",
                "conversation_flow": "main",
                "response_content": "Updated 2",
                "identifier_group": "custom",
            },
        ]
        self.mock_fs.read_file = AsyncMock(return_value=yaml.dump(yaml_content))

        await self.events.load_events_from_file("/test/path")

        # Verify file system calls
        self.mock_fs.check_if_file_exists.assert_called_once_with(
            file_name="events.yml", file_path="/test/path"
        )
        self.mock_fs.read_file.assert_called_once_with(
            file_name="events.yml", file_path="/test/path"
        )

        # Verify events were loaded
        events = self.events.get_events()
        assert len(events) == 2
        assert events[0].identifier == "test_1"
        assert events[0].event_type == "create"
        assert events[0].identifier_group == "default"
        assert events[1].identifier == "test_2"
        assert events[1].event_type == "update"
        assert events[1].identifier_group == "custom"

    @pytest.mark.asyncio
    async def test_load_events_from_file_no_file(self):
        """Test loading events when file doesn't exist"""
        self.mock_fs.check_if_file_exists = AsyncMock(return_value=False)

        # Add an existing event to test it gets cleared
        existing_event = Event(
            identifier="existing",
            event_type="create",
            file_name="existing.txt",
            conversation_flow="main",
            response_content="Existing",
        )
        self.events.add_event(existing_event)

        with patch("builtins.print") as mock_print:
            await self.events.load_events_from_file("/test/path")

        # Verify file system calls
        self.mock_fs.check_if_file_exists.assert_called_once_with(
            file_name="events.yml", file_path="/test/path"
        )
        self.mock_fs.read_file.assert_not_called()

        # Verify events were cleared and none loaded
        events = self.events.get_events()
        assert len(events) == 0

        # Verify print message
        mock_print.assert_called_with("No events.yml found at /test/path")

    @pytest.mark.asyncio
    async def test_load_events_from_file_no_fs(self):
        """Test loading events when file system is None"""
        events_no_fs = Events(None)

        # Add an existing event to test it gets cleared
        existing_event = Event(
            identifier="existing",
            event_type="create",
            file_name="existing.txt",
            conversation_flow="main",
            response_content="Existing",
        )
        events_no_fs.add_event(existing_event)

        with patch("builtins.print") as mock_print:
            await events_no_fs.load_events_from_file("/test/path")

        # Verify events were cleared and none loaded
        events = events_no_fs.get_events()
        assert len(events) == 0

        # Verify print message
        mock_print.assert_called_with("No events.yml found at /test/path")

    @pytest.mark.asyncio
    async def test_load_events_from_file_empty_yaml(self):
        """Test loading events from empty YAML file"""
        self.mock_fs.check_if_file_exists = AsyncMock(return_value=True)
        self.mock_fs.read_file = AsyncMock(return_value=yaml.dump([]))  # Empty list

        await self.events.load_events_from_file("/test/path")

        # Verify events were cleared and empty list was processed
        events = self.events.get_events()
        assert len(events) == 0

    @pytest.mark.asyncio
    async def test_load_events_from_file_value_error(self):
        """Test loading events with ValueError"""
        self.mock_fs.check_if_file_exists = AsyncMock(
            side_effect=ValueError("Test error")
        )

        with patch("builtins.print") as mock_print:
            await self.events.load_events_from_file("/test/path")

        # Verify print message includes the error
        mock_print.assert_called_with(
            "No events.yml found at /test/path and error is Test error"
        )
