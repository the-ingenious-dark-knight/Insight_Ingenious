"""
Tests for ingenious.models.file_storage_client module
"""

import pytest

from ingenious.models.file_storage_client import FileStorageClientType


class TestFileStorageClientType:
    """Test cases for FileStorageClientType enum"""

    def test_enum_values(self):
        """Test that enum has expected values"""
        assert FileStorageClientType.AZURE.value == "azure"
        assert FileStorageClientType.LOCAL.value == "local"

    def test_enum_members(self):
        """Test that enum has expected members"""
        members = list(FileStorageClientType)
        assert len(members) == 2
        assert FileStorageClientType.AZURE in members
        assert FileStorageClientType.LOCAL in members

    def test_enum_from_value(self):
        """Test creating enum instance from value"""
        azure_type = FileStorageClientType("azure")
        local_type = FileStorageClientType("local")

        assert azure_type == FileStorageClientType.AZURE
        assert local_type == FileStorageClientType.LOCAL

    def test_invalid_enum_value(self):
        """Test that invalid value raises ValueError"""
        with pytest.raises(ValueError):
            FileStorageClientType("invalid")

    def test_enum_equality(self):
        """Test enum equality comparison"""
        assert FileStorageClientType.AZURE == FileStorageClientType.AZURE
        assert FileStorageClientType.LOCAL == FileStorageClientType.LOCAL
        assert FileStorageClientType.AZURE != FileStorageClientType.LOCAL

    def test_enum_string_representation(self):
        """Test string representation of enum values"""
        assert str(FileStorageClientType.AZURE) == "FileStorageClientType.AZURE"
        assert str(FileStorageClientType.LOCAL) == "FileStorageClientType.LOCAL"

    def test_enum_membership(self):
        """Test membership testing with enum"""
        assert "azure" == FileStorageClientType.AZURE.value
        assert "local" == FileStorageClientType.LOCAL.value

    def test_enum_iteration(self):
        """Test iterating over enum values"""
        values = [member.value for member in FileStorageClientType]
        assert "azure" in values
        assert "local" in values
        assert len(values) == 2
