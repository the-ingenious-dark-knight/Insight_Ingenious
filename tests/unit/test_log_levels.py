"""
Tests for ingenious.utils.log_levels module
"""
import pytest

from ingenious.utils.log_levels import LogLevel


class TestLogLevel:
    """Test cases for LogLevel class"""

    def test_log_level_constants(self):
        """Test that log level constants have expected values"""
        assert LogLevel.DEBUG == 0
        assert LogLevel.INFO == 1
        assert LogLevel.WARNING == 2
        assert LogLevel.ERROR == 3

    def test_from_string_valid_levels(self):
        """Test from_string method with valid level strings"""
        assert LogLevel.from_string("DEBUG") == LogLevel.DEBUG
        assert LogLevel.from_string("INFO") == LogLevel.INFO
        assert LogLevel.from_string("WARNING") == LogLevel.WARNING
        assert LogLevel.from_string("ERROR") == LogLevel.ERROR

    def test_from_string_case_insensitive(self):
        """Test from_string method is case insensitive"""
        assert LogLevel.from_string("debug") == LogLevel.DEBUG
        assert LogLevel.from_string("info") == LogLevel.INFO
        assert LogLevel.from_string("warning") == LogLevel.WARNING
        assert LogLevel.from_string("error") == LogLevel.ERROR
        assert LogLevel.from_string("Debug") == LogLevel.DEBUG
        assert LogLevel.from_string("InFo") == LogLevel.INFO
        assert LogLevel.from_string("WaRnInG") == LogLevel.WARNING
        assert LogLevel.from_string("ErRoR") == LogLevel.ERROR

    def test_from_string_invalid_level(self):
        """Test from_string method with invalid level strings"""
        assert LogLevel.from_string("INVALID") is None
        assert LogLevel.from_string("TRACE") is None
        assert LogLevel.from_string("FATAL") is None
        assert LogLevel.from_string("") is None
        assert LogLevel.from_string("123") is None

    def test_from_string_with_none(self):
        """Test from_string method with None input"""
        # The str() function converts None to "None", so upper() works and returns None from mapping
        assert LogLevel.from_string(None) is None

    def test_from_string_with_non_string(self):
        """Test from_string method with non-string input"""
        assert LogLevel.from_string(123) is None
        assert LogLevel.from_string([]) is None
        assert LogLevel.from_string({}) is None

    def test_to_string_valid_levels(self):
        """Test to_string method with valid level integers"""
        assert LogLevel.to_string(LogLevel.DEBUG) == "DEBUG"
        assert LogLevel.to_string(LogLevel.INFO) == "INFO"
        assert LogLevel.to_string(LogLevel.WARNING) == "WARNING"
        assert LogLevel.to_string(LogLevel.ERROR) == "ERROR"

    def test_to_string_with_integers(self):
        """Test to_string method with integer values"""
        assert LogLevel.to_string(0) == "DEBUG"
        assert LogLevel.to_string(1) == "INFO"
        assert LogLevel.to_string(2) == "WARNING"
        assert LogLevel.to_string(3) == "ERROR"

    def test_to_string_invalid_level(self):
        """Test to_string method with invalid level integers"""
        assert LogLevel.to_string(-1) == "Unknown"
        assert LogLevel.to_string(4) == "Unknown"
        assert LogLevel.to_string(999) == "Unknown"

    def test_to_string_with_non_integer(self):
        """Test to_string method with non-integer input"""
        assert LogLevel.to_string("DEBUG") == "Unknown"
        assert LogLevel.to_string(None) == "Unknown"
        # Note: Lists and dicts are not hashable and will raise TypeError
        # when used as dictionary keys

    def test_round_trip_conversion(self):
        """Test converting from string to int and back to string"""
        test_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        
        for level_str in test_levels:
            level_int = LogLevel.from_string(level_str)
            converted_back = LogLevel.to_string(level_int)
            assert converted_back == level_str

    def test_log_levels_are_ordered(self):
        """Test that log levels are properly ordered"""
        assert LogLevel.DEBUG < LogLevel.INFO
        assert LogLevel.INFO < LogLevel.WARNING
        assert LogLevel.WARNING < LogLevel.ERROR

    def test_case_insensitive_round_trip(self):
        """Test round trip conversion with different cases"""
        lowercase_levels = ["debug", "info", "warning", "error"]
        expected_uppercase = ["DEBUG", "INFO", "WARNING", "ERROR"]
        
        for lower, upper in zip(lowercase_levels, expected_uppercase):
            level_int = LogLevel.from_string(lower)
            converted_back = LogLevel.to_string(level_int)
            assert converted_back == upper