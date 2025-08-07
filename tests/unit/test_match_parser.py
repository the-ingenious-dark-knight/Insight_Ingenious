"""
Tests for ingenious.utils.match_parser module
"""
import pytest
from datetime import datetime

from ingenious.utils.match_parser import MatchDataParser


class TestMatchDataParser:
    """Test cases for MatchDataParser class"""

    def test_init_with_defaults(self):
        """Test MatchDataParser initialization with default values"""
        parser = MatchDataParser()
        assert parser.payload is None
        assert parser.event_type is None

    def test_init_with_payload_and_event_type(self):
        """Test MatchDataParser initialization with custom values"""
        payload = {"test": "data"}
        event_type = "wicket"
        parser = MatchDataParser(payload=payload, event_type=event_type)
        assert parser.payload == payload
        assert parser.event_type == event_type

    def test_create_detailed_summary_default(self):
        """Test create_detailed_summary with default values"""
        parser = MatchDataParser()
        message, over_ball, timestamp, match_id, feed_id = parser.create_detailed_summary()
        
        assert message == "test payload"
        assert over_ball == "test_over"
        assert match_id == "test_match_123"
        assert feed_id == "test_feed_456"
        # Just verify timestamp is a string (exact value varies)
        assert isinstance(timestamp, str)

    def test_create_detailed_summary_with_payload(self):
        """Test create_detailed_summary with custom payload"""
        payload = {"player": "Smith", "runs": 4}
        parser = MatchDataParser(payload=payload)
        message, over_ball, timestamp, match_id, feed_id = parser.create_detailed_summary()
        
        assert message == str(payload)
        assert over_ball == "test_over"
        assert match_id == "test_match_123"
        assert feed_id == "test_feed_456"
        assert isinstance(timestamp, str)

    def test_create_detailed_summary_with_none_payload(self):
        """Test create_detailed_summary with None payload"""
        parser = MatchDataParser(payload=None)
        message, over_ball, timestamp, match_id, feed_id = parser.create_detailed_summary()
        
        assert message == "test payload"
        assert over_ball == "test_over"
        assert match_id == "test_match_123"
        assert feed_id == "test_feed_456"
        assert isinstance(timestamp, str)

    def test_create_detailed_summary_with_string_payload(self):
        """Test create_detailed_summary with string payload"""
        payload = "boundary hit for four"
        parser = MatchDataParser(payload=payload)
        message, over_ball, timestamp, match_id, feed_id = parser.create_detailed_summary()
        
        assert message == payload
        assert over_ball == "test_over"
        assert match_id == "test_match_123"
        assert feed_id == "test_feed_456"
        assert isinstance(timestamp, str)

    def test_create_detailed_summary_return_types(self):
        """Test that create_detailed_summary returns correct types"""
        parser = MatchDataParser()
        result = parser.create_detailed_summary()
        
        assert isinstance(result, tuple)
        assert len(result) == 5
        for item in result:
            assert isinstance(item, str)