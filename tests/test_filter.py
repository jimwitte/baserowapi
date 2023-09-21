import pytest
from baserowapi.models.filter import Filter

def test_basic_initialization_with_default_operator():
    filter_obj = Filter("Name", "John")
    assert filter_obj.field_name == "Name"
    assert filter_obj.value == "John"
    assert filter_obj.operator == "equal"

def test_basic_initialization_with_custom_operator():
    filter_obj = Filter("Age", 25, "greater_than")
    assert filter_obj.field_name == "Age"
    assert filter_obj.value == 25
    assert filter_obj.operator == "greater_than"

def test_query_string_with_simple_field_and_value():
    filter_obj = Filter("Name", "John")
    assert filter_obj.query_string == "filter__Name__equal=John"

def test_query_string_with_special_char_in_field():
    filter_obj = Filter("First Name", "John")
    assert filter_obj.query_string == "filter__First+Name__equal=John"

def test_query_string_with_special_char_in_value():
    filter_obj = Filter("URL", "https://example.com")
    assert filter_obj.query_string == "filter__URL__equal=https%3A%2F%2Fexample.com"

def test_query_string_with_special_char_in_field_and_value():
    filter_obj = Filter("User URL", "https://example.com/user?id=1")
    assert filter_obj.query_string == "filter__User+URL__equal=https%3A%2F%2Fexample.com%2Fuser%3Fid%3D1"

def test_query_string_with_different_operator():
    filter_obj = Filter("Age", 25, "less_than")
    assert filter_obj.query_string == "filter__Age__less_than=25"

def test_empty_field_name():
    with pytest.raises(ValueError):
        Filter("", "John")

