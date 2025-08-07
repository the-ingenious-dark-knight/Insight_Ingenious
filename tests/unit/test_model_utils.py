"""
Tests for ingenious.utils.model_utils module
"""
from typing import Any, Dict, List
from unittest.mock import Mock, patch
import pytest
from pydantic import BaseModel

from ingenious.utils.model_utils import (
    Is_Non_Complex_Field_Check_By_Value,
    Is_Non_Complex_Field_Check_By_Type,
    FieldData,
    Get_Model_Properties,
    Dict_To_Csv,
    List_To_Csv,
    Listable_Object_To_Csv,
    Object_To_Yaml,
    Object_To_Markdown
)


class TestIsNonComplexFieldCheckByValue:
    """Test cases for Is_Non_Complex_Field_Check_By_Value function"""
    
    def test_simple_types_return_true(self):
        """Test that simple types return True"""
        assert Is_Non_Complex_Field_Check_By_Value("string") is True
        assert Is_Non_Complex_Field_Check_By_Value(42) is True
        assert Is_Non_Complex_Field_Check_By_Value(3.14) is True
        assert Is_Non_Complex_Field_Check_By_Value(True) is True
        assert Is_Non_Complex_Field_Check_By_Value(False) is True
        assert Is_Non_Complex_Field_Check_By_Value(None) is True
    
    def test_complex_types_return_false(self):
        """Test that complex types return False"""
        assert Is_Non_Complex_Field_Check_By_Value([1, 2, 3]) is False
        assert Is_Non_Complex_Field_Check_By_Value({"key": "value"}) is False
        assert Is_Non_Complex_Field_Check_By_Value(object()) is False
        assert Is_Non_Complex_Field_Check_By_Value(lambda x: x) is False


class TestIsNonComplexFieldCheckByType:
    """Test cases for Is_Non_Complex_Field_Check_By_Type function"""
    
    def test_type_without_root_model_returns_true(self):
        """Test that types without RootModel return True"""
        assert Is_Non_Complex_Field_Check_By_Type("str") is True
        assert Is_Non_Complex_Field_Check_By_Type("int") is True
        assert Is_Non_Complex_Field_Check_By_Type("List[str]") is True
    
    def test_type_with_root_model_returns_false(self):
        """Test that types with RootModel return False"""
        assert Is_Non_Complex_Field_Check_By_Type("RootModel[str]") is False
        assert Is_Non_Complex_Field_Check_By_Type("SomeRootModel") is False
    
    def test_custom_root_model_name(self):
        """Test with custom root model name"""
        assert Is_Non_Complex_Field_Check_By_Type("CustomRoot[str]", "CustomRoot") is False
        assert Is_Non_Complex_Field_Check_By_Type("RootModel[str]", "CustomRoot") is True


class TestFieldData:
    """Test cases for FieldData model"""
    
    def test_field_data_creation(self):
        """Test creating FieldData instance"""
        field = FieldData(FieldName="test_field", FieldType="str")
        assert field.FieldName == "test_field"
        assert field.FieldType == "str"
    
    def test_field_data_required_fields(self):
        """Test that required fields are enforced"""
        with pytest.raises(Exception):  # Pydantic validation error
            FieldData(FieldName="test")  # Missing FieldType


class SampleModel(BaseModel):
    """Sample model for testing Get_Model_Properties"""
    name: str
    age: int
    active: bool


class TestGetModelProperties:
    """Test cases for Get_Model_Properties function"""
    
    def test_get_model_properties(self):
        """Test getting properties from a model"""
        properties = Get_Model_Properties(SampleModel)
        
        assert len(properties) == 3
        
        # Check that all expected fields are present
        field_names = [prop.FieldName for prop in properties]
        assert "name" in field_names
        assert "age" in field_names  
        assert "active" in field_names
        
        # Check that FieldData objects are returned
        for prop in properties:
            assert isinstance(prop, FieldData)
            assert isinstance(prop.FieldName, str)
            assert isinstance(prop.FieldType, str)


class TestDictToCsv:
    """Test cases for Dict_To_Csv function"""
    
    def test_dict_to_csv_basic(self):
        """Test basic Dict_To_Csv functionality"""
        data = {
            "row1": {"name": "Alice", "age": 25},
            "row2": {"name": "Bob", "age": 30}
        }
        headers = ["name", "age"]
        
        result = Dict_To_Csv(data, headers, "test")
        
        assert result.startswith("``` csv\n")
        assert result.endswith("\n```")
        assert "name,age" in result
        assert "Alice,25" in result
        assert "Bob,30" in result
    
    def test_dict_to_csv_empty_data(self):
        """Test Dict_To_Csv with empty data"""
        data = {}
        headers = ["name", "age"]
        
        result = Dict_To_Csv(data, headers, "empty")
        
        assert result.startswith("``` csv\n")
        assert result.endswith("\n```")
        assert "name,age" in result
    
    def test_dict_to_csv_missing_keys(self):
        """Test Dict_To_Csv with missing keys in data"""
        data = {
            "row1": {"name": "Alice"}  # Missing age
        }
        headers = ["name", "age"]
        
        with pytest.raises(KeyError):
            Dict_To_Csv(data, headers, "test")


class TestListToCsv:
    """Test cases for List_To_Csv function"""
    
    def test_list_to_csv_with_dicts(self):
        """Test List_To_Csv with list of dictionaries"""
        data = [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30}
        ]
        headers = ["name", "age"]
        
        result = List_To_Csv(data, headers, "test")
        
        assert result.startswith("``` csv\n")
        assert result.endswith("\n```")
        assert "name,age" in result
        assert "Alice,25" in result
        assert "Bob,30" in result
    
    def test_list_to_csv_with_objects(self):
        """Test List_To_Csv with objects that have __dict__"""
        class Person:
            def __init__(self, name: str, age: int):
                self.name = name
                self.age = age
        
        data = [Person("Alice", 25), Person("Bob", 30)]
        headers = ["name", "age"]
        
        result = List_To_Csv(data, headers, "test")
        
        assert result.startswith("``` csv\n")
        assert result.endswith("\n```")
        assert "name,age" in result
        assert "Alice,25" in result
        assert "Bob,30" in result
    
    def test_list_to_csv_with_unconvertible_objects(self):
        """Test List_To_Csv with objects that can't be converted to dict - targets lines 56-59"""
        class BadObject:
            def __init__(self):
                pass
            
            @property
            def __dict__(self):
                raise AttributeError("No __dict__ available")
        
        data = [BadObject()]
        headers = ["name"]
        
        with patch('builtins.print') as mock_print:
            with pytest.raises(TypeError):  # Will fail when trying to subscript BadObject
                List_To_Csv(data, headers, "test")
            
            # Should have printed the error message (line 59)
            mock_print.assert_called()
            call_args = mock_print.call_args[0][0]
            assert "Could not convert" in call_args
    
    def test_list_to_csv_empty_list(self):
        """Test List_To_Csv with empty list"""
        data = []
        headers = ["name", "age"]
        
        result = List_To_Csv(data, headers, "empty")
        
        assert result.startswith("``` csv\n")
        assert result.endswith("\n```")
        assert "name,age" in result


class TestListableObjectToCsv:
    """Test cases for Listable_Object_To_Csv function"""
    
    def test_listable_object_to_csv(self):
        """Test Listable_Object_To_Csv functionality"""
        sample_data = [
            SampleModel(name="Alice", age=25, active=True),
            SampleModel(name="Bob", age=30, active=False)
        ]
        
        result = Listable_Object_To_Csv(sample_data, SampleModel)
        
        assert result.startswith("``` csv\n")
        assert result.endswith("\n```")
        assert "name,age,active" in result
        assert "Alice,25,True" in result
        assert "Bob,30,False" in result
    
    def test_listable_object_to_csv_with_missing_attributes(self):
        """Test Listable_Object_To_Csv with objects missing some attributes"""
        class IncompleteObject:
            def __init__(self, name: str):
                self.name = name
                # Missing age and active attributes
        
        data = [IncompleteObject("Alice")]
        
        result = Listable_Object_To_Csv(data, SampleModel)
        
        assert result.startswith("``` csv\n")
        assert result.endswith("\n```")
        assert "Alice,," in result  # Missing attributes become empty in CSV
    
    def test_listable_object_to_csv_empty_list(self):
        """Test Listable_Object_To_Csv with empty list"""
        result = Listable_Object_To_Csv([], SampleModel)
        
        assert result.startswith("``` csv\n")
        assert result.endswith("\n```")
        assert "name,age,active" in result


class TestObjectToYaml:
    """Test cases for Object_To_Yaml function"""
    
    def test_object_to_yaml_basic(self):
        """Test basic Object_To_Yaml functionality - targets lines 82-91"""
        class TestObject:
            def __init__(self):
                self.name = "test"
                self.value = 42
                self.active = True
        
        obj = TestObject()
        result = Object_To_Yaml(obj)
        
        assert result.startswith("``` yaml\n")
        assert result.endswith("\n```")
        assert "name: test" in result
        assert "value: 42" in result
        assert "active: true" in result
    
    def test_object_to_yaml_strip_complex_fields(self):
        """Test Object_To_Yaml with strip_complex_fields=True - targets lines 84-89"""
        class TestObject:
            def __init__(self):
                self.name = "test"  # Simple field
                self.value = 42     # Simple field
                self.complex_list = [1, 2, 3]  # Complex field
                self.complex_dict = {"key": "value"}  # Complex field
        
        obj = TestObject()
        result = Object_To_Yaml(obj, strip_complex_fields=True)
        
        assert result.startswith("``` yaml\n")
        assert result.endswith("\n```")
        assert "name: test" in result
        assert "value: 42" in result
        # Complex fields should be stripped
        assert "complex_list" not in result
        assert "complex_dict" not in result
    
    def test_object_to_yaml_no_strip_complex_fields(self):
        """Test Object_To_Yaml with strip_complex_fields=False (default)"""
        class TestObject:
            def __init__(self):
                self.name = "test"
                self.complex_list = [1, 2, 3]
        
        obj = TestObject()
        result = Object_To_Yaml(obj, strip_complex_fields=False)
        
        assert result.startswith("``` yaml\n")
        assert result.endswith("\n```")
        assert "name: test" in result
        assert "complex_list:" in result  # Complex fields should be included


class TestObjectToMarkdown:
    """Test cases for Object_To_Markdown function"""
    
    def test_object_to_markdown(self):
        """Test Object_To_Markdown functionality"""
        class TestObject:
            def __init__(self):
                self.name = "test"
                self.value = 42
        
        obj = TestObject()
        result = Object_To_Markdown(obj, "test_object")
        
        # Should return jsonpickle serialized string
        assert isinstance(result, str)
        assert len(result) > 0
        # jsonpickle output should contain class information
        assert "py/object" in result or result.startswith("{")
    
    def test_object_to_markdown_complex_object(self):
        """Test Object_To_Markdown with complex object"""
        data = {
            "name": "test",
            "items": [1, 2, 3],
            "nested": {"key": "value"}
        }
        
        result = Object_To_Markdown(data, "complex")
        
        assert isinstance(result, str)
        assert len(result) > 0
        # Should contain the data in some form
        assert "test" in result
    
    def test_object_to_markdown_name_parameter_unused(self):
        """Test that the name parameter doesn't affect the output"""
        obj = {"test": "value"}
        
        result1 = Object_To_Markdown(obj, "name1")
        result2 = Object_To_Markdown(obj, "name2")
        
        # Name parameter is not used in the function, so results should be same
        assert result1 == result2