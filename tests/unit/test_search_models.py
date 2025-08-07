"""
Tests for ingenious.models.search module
"""
import pytest
from pydantic import ValidationError

from ingenious.models.search import SearchQuery, SearchResult


class TestSearchQuery:
    """Test cases for SearchQuery model"""

    def test_init_with_valid_data(self):
        """Test SearchQuery initialization with valid data"""
        query = SearchQuery(query="test query", top=10)
        assert query.query == "test query"
        assert query.top == 10

    def test_init_with_missing_query(self):
        """Test SearchQuery initialization fails without query"""
        with pytest.raises(ValidationError):
            SearchQuery(top=10)

    def test_init_with_missing_top(self):
        """Test SearchQuery initialization fails without top"""
        with pytest.raises(ValidationError):
            SearchQuery(query="test query")

    def test_query_must_be_string(self):
        """Test that query field must be a string"""
        with pytest.raises(ValidationError):
            SearchQuery(query=123, top=10)

    def test_top_can_be_coerced_from_string(self):
        """Test that top field can be coerced from string to int"""
        query = SearchQuery(query="test", top="10")
        assert query.top == 10

    def test_model_serialization(self):
        """Test SearchQuery can be serialized to dict"""
        query = SearchQuery(query="test query", top=5)
        data = query.model_dump()
        assert data == {"query": "test query", "top": 5}

    def test_model_validation_from_dict(self):
        """Test SearchQuery can be created from dict"""
        data = {"query": "test query", "top": 15}
        query = SearchQuery(**data)
        assert query.query == "test query"
        assert query.top == 15


class TestSearchResult:
    """Test cases for SearchResult model"""

    def test_init_with_valid_data(self):
        """Test SearchResult initialization with valid data"""
        results_data = [{"id": 1, "name": "test"}, {"id": 2, "name": "test2"}]
        result = SearchResult(results=results_data)
        assert result.results == results_data

    def test_init_with_empty_results(self):
        """Test SearchResult with empty results list"""
        result = SearchResult(results=[])
        assert result.results == []

    def test_init_with_missing_results(self):
        """Test SearchResult initialization fails without results"""
        with pytest.raises(ValidationError):
            SearchResult()

    def test_results_must_be_list(self):
        """Test that results field must be a list"""
        with pytest.raises(ValidationError):
            SearchResult(results="not a list")

    def test_results_with_various_dict_structures(self):
        """Test SearchResult accepts various dictionary structures"""
        various_results = [
            {"simple": "value"},
            {"nested": {"key": "value"}},
            {"list_value": [1, 2, 3]},
            {"mixed": {"string": "val", "number": 42, "bool": True}}
        ]
        result = SearchResult(results=various_results)
        assert result.results == various_results

    def test_model_serialization(self):
        """Test SearchResult can be serialized to dict"""
        results_data = [{"id": 1, "name": "test"}]
        result = SearchResult(results=results_data)
        data = result.model_dump()
        assert data == {"results": results_data}

    def test_model_validation_from_dict(self):
        """Test SearchResult can be created from dict"""
        results_data = [{"id": 1, "name": "test"}]
        data = {"results": results_data}
        result = SearchResult(**data)
        assert result.results == results_data