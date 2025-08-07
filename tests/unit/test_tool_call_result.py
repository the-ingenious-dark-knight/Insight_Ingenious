"""
Tests for ingenious.models.tool_call_result module
"""
import pytest
from pydantic import ValidationError

from ingenious.models.tool_call_result import (
    ToolCallResult,
    ProductToolCallResult,
    KnowledgeBaseToolCallResult,
    ActionToolCallResult
)
from ingenious.models.chat import Action, KnowledgeBaseLink, Product


class TestToolCallResult:
    """Test cases for ToolCallResult model"""

    def test_init_with_valid_data(self):
        """Test ToolCallResult initialization with valid data"""
        result = ToolCallResult(results="test result")
        assert result.results == "test result"

    def test_init_with_missing_results(self):
        """Test ToolCallResult initialization fails without results"""
        with pytest.raises(ValidationError):
            ToolCallResult()

    def test_results_must_be_string(self):
        """Test that results field must be a string"""
        with pytest.raises(ValidationError):
            ToolCallResult(results=123)

    def test_model_serialization(self):
        """Test ToolCallResult can be serialized to dict"""
        result = ToolCallResult(results="test result")
        data = result.model_dump()
        assert data == {"results": "test result"}


class TestProductToolCallResult:
    """Test cases for ProductToolCallResult model"""

    def test_init_with_valid_data(self):
        """Test ProductToolCallResult initialization with valid data"""
        products = [
            Product(name="Product 1", id="p1", description="Description 1"),
            Product(name="Product 2", id="p2", description="Description 2")
        ]
        result = ProductToolCallResult(results="Found products", products=products)
        assert result.results == "Found products"
        assert result.products == products

    def test_init_with_empty_products(self):
        """Test ProductToolCallResult with empty products list"""
        result = ProductToolCallResult(results="No products", products=[])
        assert result.results == "No products"
        assert result.products == []

    def test_init_with_missing_products(self):
        """Test ProductToolCallResult initialization fails without products"""
        with pytest.raises(ValidationError):
            ProductToolCallResult(results="test")

    def test_inherits_from_tool_call_result(self):
        """Test that ProductToolCallResult inherits from ToolCallResult"""
        products = [Product(name="Product 1", id="p1", description="Description 1")]
        result = ProductToolCallResult(results="Found products", products=products)
        assert isinstance(result, ToolCallResult)


class TestKnowledgeBaseToolCallResult:
    """Test cases for KnowledgeBaseToolCallResult model"""

    def test_init_with_valid_data(self):
        """Test KnowledgeBaseToolCallResult initialization with valid data"""
        kb_links = [
            KnowledgeBaseLink(title="Link 1", url="http://example.com/1"),
            KnowledgeBaseLink(title="Link 2", url="http://example.com/2")
        ]
        result = KnowledgeBaseToolCallResult(results="Found links", knowledge_base_links=kb_links)
        assert result.results == "Found links"
        assert result.knowledge_base_links == kb_links

    def test_init_with_empty_knowledge_base_links(self):
        """Test KnowledgeBaseToolCallResult with empty knowledge base links list"""
        result = KnowledgeBaseToolCallResult(results="No links", knowledge_base_links=[])
        assert result.results == "No links"
        assert result.knowledge_base_links == []

    def test_init_with_missing_knowledge_base_links(self):
        """Test KnowledgeBaseToolCallResult initialization fails without knowledge_base_links"""
        with pytest.raises(ValidationError):
            KnowledgeBaseToolCallResult(results="test")

    def test_inherits_from_tool_call_result(self):
        """Test that KnowledgeBaseToolCallResult inherits from ToolCallResult"""
        kb_links = [KnowledgeBaseLink(title="Link 1", url="http://example.com/1")]
        result = KnowledgeBaseToolCallResult(results="Found links", knowledge_base_links=kb_links)
        assert isinstance(result, ToolCallResult)


class TestActionToolCallResult:
    """Test cases for ActionToolCallResult model"""

    def test_init_with_valid_data(self):
        """Test ActionToolCallResult initialization with valid data"""
        actions = [
            Action(name="Action 1", description="Description 1"),
            Action(name="Action 2", description="Description 2")
        ]
        result = ActionToolCallResult(results="Found actions", actions=actions)
        assert result.results == "Found actions"
        assert result.actions == actions

    def test_init_with_empty_actions(self):
        """Test ActionToolCallResult with empty actions list"""
        result = ActionToolCallResult(results="No actions", actions=[])
        assert result.results == "No actions"
        assert result.actions == []

    def test_init_with_missing_actions(self):
        """Test ActionToolCallResult initialization fails without actions"""
        with pytest.raises(ValidationError):
            ActionToolCallResult(results="test")

    def test_inherits_from_tool_call_result(self):
        """Test that ActionToolCallResult inherits from ToolCallResult"""
        actions = [Action(name="Action 1", description="Description 1")]
        result = ActionToolCallResult(results="Found actions", actions=actions)
        assert isinstance(result, ToolCallResult)