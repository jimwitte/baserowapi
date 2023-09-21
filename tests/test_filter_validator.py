import pytest
from baserowapi.validators.filter_validator import FilterValidator

# Mock table fixture
@pytest.fixture
def mock_table():
    class MockTable:
        def get_field_names(self):
            return ['name', 'age', 'email']
        
        def get_field_type(self, field_name):
            if field_name == 'name':
                return 'text'
            elif field_name == 'age':
                return 'number'
            elif field_name == 'email':
                return 'email'
            else:
                return None

    return MockTable()

# Filter object fixture
@pytest.fixture
def mock_filter():
    class MockFilter:
        def __init__(self, field_name=None, value=None, operator=None):  # Default values set to None for easy testing of missing attributes.
            self.field_name = field_name
            self.value = value
            self.operator = operator

    return MockFilter

def test_validate_filters_with_non_list_input(mock_table):
    with pytest.raises(ValueError, match="^'filters' must be a list.$"):
        FilterValidator.validate_filters_against_table("I'm not a list", mock_table)

# Mock filter object missing field_name
@pytest.fixture
def mock_filter_missing_field_name():
    class MockFilterMissingFieldName:
        def __init__(self, value=None, operator=None):
            self.value = value
            self.operator = operator

    return MockFilterMissingFieldName

# Mock filter object missing operator
@pytest.fixture
def mock_filter_missing_operator():
    class MockFilterMissingOperator:
        def __init__(self, field_name=None, value=None):
            self.field_name = field_name
            self.value = value

    return MockFilterMissingOperator

def test_validate_filters_missing_field_name(mock_table, mock_filter_missing_field_name):
    filter_with_missing_field_name = mock_filter_missing_field_name(operator="contains", value="John")
    
    with pytest.raises(ValueError, match="^All items in 'filters' must have 'field_name' and 'operator' attributes.$"):
        FilterValidator.validate_filters_against_table([filter_with_missing_field_name], mock_table)

def test_validate_filters_missing_operator(mock_table, mock_filter_missing_operator):
    filter_with_missing_operator = mock_filter_missing_operator(field_name="name", value="John")
    
    with pytest.raises(ValueError, match="^All items in 'filters' must have 'field_name' and 'operator' attributes.$"):
        FilterValidator.validate_filters_against_table([filter_with_missing_operator], mock_table)

def test_validate_filters_with_valid_filters(mock_table, mock_filter):
    # Define a list of valid filters
    valid_filters = [
        mock_filter(field_name="name", value="John", operator="contains"),
        mock_filter(field_name="age", value=25, operator="equal"),
        mock_filter(field_name="email", value="john@example.com", operator="contains")
    ]
    
    # Try validating the filters. This should not raise any exceptions.
    FilterValidator.validate_filters_against_table(valid_filters, mock_table)

def test_single_filter_validation_invalid(mock_table, mock_filter):
    # Using an unsupported operator
    invalid_operator_filter = mock_filter(field_name="name", value="John", operator="unsupported_operator")
    with pytest.raises(ValueError, match="^Invalid filter 'unsupported_operator' with value 'John' for field type 'text'$"):
        FilterValidator.validate_filters_against_table([invalid_operator_filter], mock_table)

    # Using a field name that isn't present in the table
    invalid_field_name_filter = mock_filter(field_name="invalid_field", value="John", operator="contains")
    with pytest.raises(ValueError, match="^Invalid field name in filter: invalid_field$"):
        FilterValidator.validate_filters_against_table([invalid_field_name_filter], mock_table)

    # Providing a value that's incompatible with the field type
    # For demonstration, using a string value for the 'age' field which is of type 'number'.
    incompatible_value_filter = mock_filter(field_name="age", value="John", operator="equals")
    with pytest.raises(ValueError, match="^Invalid filter 'equals' with value 'John' for field type 'number'$"):
        FilterValidator.validate_filters_against_table([incompatible_value_filter], mock_table)

def test_single_filter_validation_valid(mock_table, mock_filter):
    # A text field with a valid 'contains' operator
    valid_text_filter = mock_filter(field_name="name", value="John", operator="contains")
    FilterValidator.validate_filters_against_table([valid_text_filter], mock_table)

    # A number field with a valid 'equals' operator
    valid_number_filter = mock_filter(field_name="age", value=25, operator="equal")
    FilterValidator.validate_filters_against_table([valid_number_filter], mock_table)

    # An email field with a valid 'contains' operator
    valid_email_filter = mock_filter(field_name="email", value="example@", operator="contains")
    FilterValidator.validate_filters_against_table([valid_email_filter], mock_table)

    # Combining multiple valid filters
    multiple_valid_filters = [
        mock_filter(field_name="name", value="John", operator="contains"),
        mock_filter(field_name="age", value=30, operator="equal"),
        mock_filter(field_name="email", value="@domain.com", operator="contains")
    ]
    FilterValidator.validate_filters_against_table(multiple_valid_filters, mock_table)

def test_single_filter_validation_missing_field_type(mock_table, mock_filter):
    # Field 'address' doesn't exist in the mock table
    filter_with_missing_field_type = mock_filter(field_name="address", value="123 St.", operator="contains")
    
    with pytest.raises(ValueError, match="^Invalid field name in filter: address$"):
        FilterValidator.validate_filters_against_table([filter_with_missing_field_type], mock_table)
