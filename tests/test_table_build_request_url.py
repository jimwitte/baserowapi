import pytest
from baserowapi.baserow import Baserow
from baserowapi.models.table import Table
from baserowapi.models.row import Row
from baserowapi.models.filter import Filter
import urllib.parse

@pytest.fixture
def mock_client(mocker):
    client = Baserow()
    mocker.patch.object(client, 'make_api_request', return_value={})
    return client

@pytest.fixture
def mock_table(mock_client, mocker):
    table = Table(client=mock_client, table_id=123)
    mocker.patch.object(Table, 'fields', return_value={"Name": {"name": "Name", "type": "text"}})
    return table

def test_parse_row_data_with_valid_dict_input(mock_table):
    # Mock input row data based on Baserow API response format
    row_data_input = {
        "count": 1024,
        "next": "https://api.baserow.io/api/database/rows/table/195388/?page=2",
        "previous": None,
        "results": [
            {
                "id": 0,
                "order": "1.00000000000000000000",
                "Name": "string",
                "Last name": "string",
                "Notes": "string",
                "Active": True
            }
        ]
    }
    
    # Call the _parse_row_data method
    parsed_rows = mock_table._parse_row_data(row_data_input)
    
    # Validate parsed row
    assert len(parsed_rows) == 1
    assert isinstance(parsed_rows[0], Row)
    assert parsed_rows[0]['Name'] == "string"
    assert parsed_rows[0]['Last name'] == "string"
    assert parsed_rows[0]['Notes'] == "string"
    assert parsed_rows[0]['Active'] is True

def test_parse_row_data_with_invalid_dict_input(mock_table):
    # Mock input row data with an invalid format (missing "results" key, for instance)
    row_data_input = {
        "count": 1024,
        "next": "https://api.baserow.io/api/database/rows/table/195388/?page=2",
        "previous": None,
        "invalid_key": [
            {
                "id": 0,
                "order": "1.00000000000000000000",
                "Name": "string",
                "Last name": "string",
                "Notes": "string",
                "Active": True
            }
        ]
    }
    
    # Call the _parse_row_data method
    parsed_rows = mock_table._parse_row_data(row_data_input)
    
    # Validate parsed row
    assert parsed_rows == []

def test_parse_row_data_with_invalid_input_type(mock_table):
    # Mock input row data as a list, which is an invalid type for this function
    row_data_input = [
        {
            "id": 0,
            "order": "1.00000000000000000000",
            "Name": "string",
            "Last name": "string",
            "Notes": "string",
            "Active": True
        }
    ]
    
    # Call the _parse_row_data method
    parsed_rows = mock_table._parse_row_data(row_data_input)
    
    # Validate parsed row
    assert parsed_rows == []

def test_parse_row_data_with_empty_results_key(mock_table):
    # Mock input row data with an empty "results" key
    row_data_input = {
        "count": 0,
        "next": None,
        "previous": None,
        "results": []
    }
    
    # Call the _parse_row_data method
    parsed_rows = mock_table._parse_row_data(row_data_input)
    
    # Validate parsed row
    assert parsed_rows == []

def test_parse_row_data_with_none_input(mock_table):
    # Mock input row data as None
    row_data_input = None
    
    # Call the _parse_row_data method
    parsed_rows = mock_table._parse_row_data(row_data_input)
    
    # Validate parsed row
    assert parsed_rows == []

def test_build_request_url_with_no_parameters(mock_table):
    # Call the _build_request_url method with no parameters
    request_url = mock_table._build_request_url()

    # Validate the constructed URL
    expected_url = f"/api/database/rows/table/{mock_table.table_id}/?user_field_names=true"
    assert request_url == expected_url

def test_build_request_url_with_include_parameter(mock_table):
    # Fields to include
    include_fields = ['Name', 'Last name']

    # Call the _build_request_url method with the include parameter
    request_url = mock_table._build_request_url(include=include_fields)

    # Prepare the expected part of the URL for the include parameter
    encoded_include = urllib.parse.quote(','.join(include_fields))
    expected_include_part = f"include={encoded_include}"

    # Validate the constructed URL
    base_url = f"/api/database/rows/table/{mock_table.table_id}/?user_field_names=true"
    expected_url = f"{base_url}&{expected_include_part}"
    assert request_url == expected_url

def test_build_request_url_with_exclude_parameter(mock_table):
    # Fields to exclude
    exclude_fields = ['Name', 'Last name']

    # Call the _build_request_url method with the exclude parameter
    request_url = mock_table._build_request_url(exclude=exclude_fields)

    # Prepare the expected part of the URL for the exclude parameter
    encoded_exclude = urllib.parse.quote(','.join(exclude_fields))
    expected_exclude_part = f"exclude={encoded_exclude}"

    # Validate the constructed URL
    base_url = f"/api/database/rows/table/{mock_table.table_id}/?user_field_names=true"
    expected_url = f"{base_url}&{expected_exclude_part}"
    assert request_url == expected_url

def test_build_request_url_with_both_include_and_exclude(mock_table):
    # Fields to include and exclude
    include_fields = ['Name', 'Age']
    exclude_fields = ['Last name', 'Address']

    # Call the _build_request_url method with both parameters
    request_url = mock_table._build_request_url(include=include_fields, exclude=exclude_fields)

    # Prepare the expected parts of the URL for the include and exclude parameters
    encoded_include = urllib.parse.quote(','.join(include_fields))
    expected_include_part = f"include={encoded_include}"
    
    encoded_exclude = urllib.parse.quote(','.join(exclude_fields))
    expected_exclude_part = f"exclude={encoded_exclude}"

    # Validate the constructed URL
    base_url = f"/api/database/rows/table/{mock_table.table_id}/?user_field_names=true"
    expected_url = f"{base_url}&{expected_include_part}&{expected_exclude_part}"
    assert request_url == expected_url

def test_build_request_url_with_search_parameter(mock_table):
    # Define a search query
    search_query = "John Smith"

    # Call the _build_request_url method with the search parameter
    request_url = mock_table._build_request_url(search=search_query)

    # Prepare the expected part of the URL for the search parameter
    encoded_search = urllib.parse.quote(search_query)
    expected_search_part = f"search={encoded_search}"

    # Validate the constructed URL
    base_url = f"/api/database/rows/table/{mock_table.table_id}/?user_field_names=true"
    expected_url = f"{base_url}&{expected_search_part}"
    assert request_url == expected_url

def test_build_request_url_with_order_by_parameter(mock_table):
    # Define a list of fields to order by
    order_fields = ["Name", "Last name"]

    # Call the _build_request_url method with the order_by parameter
    request_url = mock_table._build_request_url(order_by=order_fields)

    # Prepare the expected part of the URL for the order_by parameter
    encoded_order = urllib.parse.quote(','.join(order_fields))
    expected_order_part = f"order_by={encoded_order}"

    # Validate the constructed URL
    base_url = f"/api/database/rows/table/{mock_table.table_id}/?user_field_names=true"
    expected_url = f"{base_url}&{expected_order_part}"
    assert request_url == expected_url

def test_build_request_url_with_view_id_parameter(mock_table):
    # Define a view ID for testing
    test_view_id = 12345

    # Call the _build_request_url method with the view_id parameter
    request_url = mock_table._build_request_url(view_id=test_view_id)

    # Prepare the expected part of the URL for the view_id parameter
    expected_view_part = f"view_id={test_view_id}"

    # Validate the constructed URL
    base_url = f"/api/database/rows/table/{mock_table.table_id}/?user_field_names=true"
    expected_url = f"{base_url}&{expected_view_part}"
    assert request_url == expected_url

def test_build_request_url_with_page_size_parameter(mock_table):
    # Define a page size for testing
    test_page_size = 50

    # Call the _build_request_url method with the page_size parameter
    request_url = mock_table._build_request_url(page_size=test_page_size)

    # Prepare the expected part of the URL for the page_size parameter
    expected_page_size_part = f"page_size={test_page_size}"

    # Validate the constructed URL
    base_url = f"/api/database/rows/table/{mock_table.table_id}/?user_field_names=true"
    expected_url = f"{base_url}&{expected_page_size_part}"
    assert request_url == expected_url

class MockBaserow:
    """
    Mocks the Baserow client. You can expand on this if needed.
    """
    def make_api_request(self, endpoint, method="GET", data=None):
        """
        Mock the API request method.
        """
        # For simplicity, return a mocked response. Expand as needed.
        return {}

class MockFilter:
    def __init__(self, field_name, operator, value):
        self.field_name = field_name
        self.operator = operator
        self.value = value

    @property
    def query_string(self):
        field_name_encoded = urllib.parse.quote(self.field_name.replace(" ", "+"))
        return f"filter__{field_name_encoded}__{self.operator}={self.value}"

class MockTable(Table):
    # Override the get_field_names() method
    def get_field_names(self):
        return ["Last name","First name"]  # Modify this list based on the filters you'll test

    # Override the get_field_type() method
    def get_field_type(self, field_name):
        # For simplicity, assume all fields are of type 'text'
        return "text"

def test_build_request_url_with_filters_parameter():
    mock_client = MockBaserow()
    mock_table = MockTable(123, mock_client)

    # Create mock filters
    mock_filters = [
        MockFilter("Last name", "equal", "Hopper")
        # Add more mock filters if necessary for further validation
    ]

    # Call the _build_request_url method with the filters parameter
    request_url = mock_table._build_request_url(filters=mock_filters)

    # Prepare the expected URL parts based on the mock filters
    expected_filter_parts = [f.query_string for f in mock_filters]

    # Validate the constructed URL
    base_url = f"/api/database/rows/table/{mock_table.table_id}/?user_field_names=true"
    expected_url = f"{base_url}&{'&'.join(expected_filter_parts)}"
    assert request_url == expected_url

def test_build_request_url_with_filter_type_parameter(mock_table):
    # Define a filter_type for testing
    test_filter_type = "OR"

    # Call the _build_request_url method with the filter_type parameter
    request_url = mock_table._build_request_url(filter_type=test_filter_type)

    # Prepare the expected part of the URL for the filter_type parameter
    expected_filter_type_part = f"filter_type={test_filter_type}"

    # Validate the constructed URL
    base_url = f"/api/database/rows/table/{mock_table.table_id}/?user_field_names=true"
    expected_url = f"{base_url}&{expected_filter_type_part}"
    assert request_url == expected_url

def test_build_request_url_with_multiple_parameters():
    mock_client = MockBaserow()
    mock_table = MockTable(123, mock_client)

    # Create mock filters
    mock_filters = [
        MockFilter("Last name", "equal", "Hopper"),
        MockFilter("First name", "equal", "Grace")
    ]

    # Define other parameters for testing
    test_filter_type = "OR"
    test_order_by = ["Last name", "First name"]

    # Call the _build_request_url method with multiple parameters
    request_url = mock_table._build_request_url(
        filters=mock_filters, 
        filter_type=test_filter_type,
        order_by=test_order_by
    )

    # Prepare the expected URL parts based on the mock filters and other parameters
    expected_filter_parts = [f.query_string for f in mock_filters]
    encoded_order_by = urllib.parse.quote(','.join(test_order_by))
    expected_order_by_part = f"order_by={encoded_order_by}"
    expected_filter_type_part = f"filter_type={test_filter_type}"

    # Validate the constructed URL
    base_url = f"/api/database/rows/table/{mock_table.table_id}/?user_field_names=true"
    expected_url = f"{base_url}&{expected_order_by_part}&{'&'.join(expected_filter_parts)}&{expected_filter_type_part}"
    assert request_url == expected_url

def test_build_request_url_with_invalid_include_parameter_type(mock_table):
    with pytest.raises(ValueError, match="'include' parameter should be a list of field names."):
        mock_table._build_request_url(include="not_a_list")

def test_build_request_url_with_invalid_exclude_parameter_type(mock_table):
    with pytest.raises(ValueError, match="'exclude' parameter should be a list of field names."):
        mock_table._build_request_url(exclude="not_a_list")

def test_build_request_url_with_invalid_order_by_parameter_type(mock_table):
    with pytest.raises(ValueError, match="order_by parameter should be a list"):
        mock_table._build_request_url(order_by="not_a_list")

def test_build_request_url_with_invalid_filters_parameter_type(mock_table):
    with pytest.raises(Exception, match=f"Failed filter validation for table {mock_table.table_id}."):
        mock_table._build_request_url(filters="not_a_list")

def test_build_request_url_with_invalid_filter_type_value(mock_table):
    invalid_filter_type = "INVALID"
    with pytest.raises(ValueError, match=f"'filter_type' should be either 'AND' or 'OR'."):
        mock_table._build_request_url(filter_type=invalid_filter_type)

def test_build_request_url_with_valid_search_value(mock_table):
    valid_search = "test_search"
    # This test assumes that no exception is raised if the value is valid
    try:
        url = mock_table._build_request_url(search=valid_search)
        assert f"search={valid_search}" in url
    except Exception as e:
        pytest.fail(f"Expected no exception, but got: {e}")

def test_build_request_url_with_valid_view_id_value(mock_table):
    valid_view_id = 123
    try:
        url = mock_table._build_request_url(view_id=valid_view_id)
        assert f"view_id={valid_view_id}" in url
    except Exception as e:
        pytest.fail(f"Expected no exception, but got: {e}")

def test_build_request_url_with_valid_page_size_value(mock_table):
    valid_page_size = 50
    try:
        url = mock_table._build_request_url(page_size=valid_page_size)
        assert f"page_size={valid_page_size}" in url
    except Exception as e:
        pytest.fail(f"Expected no exception, but got: {e}")

def test_build_request_url_with_invalid_search_type(mock_table):
    invalid_search = 123  # Using an integer instead of a string
    with pytest.raises(ValueError, match="'search' parameter should be a string."):
        mock_table._build_request_url(search=invalid_search)

def test_build_request_url_with_invalid_view_id_type(mock_table):
    invalid_view_id = "invalid_id"  # Using a string instead of an integer
    with pytest.raises(ValueError, match="'view_id' parameter should be an integer."):
        mock_table._build_request_url(view_id=invalid_view_id)

def test_build_request_url_with_invalid_page_size_type(mock_table):
    invalid_page_size = "invalid_size"  # Using a string instead of an integer
    with pytest.raises(ValueError, match="'page_size' parameter should be an integer."):
        mock_table._build_request_url(page_size=invalid_page_size)
