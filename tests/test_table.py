import pytest
from baserowapi.baserow import Baserow
from baserowapi.models.table import Table
from baserowapi.models.row import Row
from baserowapi.models.field import Field, FieldList

# Mocking the make_api_request function
@pytest.fixture
def mock_make_api_request(mocker):
    return mocker.patch.object(Baserow, 'make_api_request', autospec=True)

def test_fields_successfully_fetches_data(mock_make_api_request):

    example_data = [
        {
            "id": 1316804,
            "table_id": 195388,
            "name": "Name",
            "order": 0,
            "type": "text",
            "primary": True,
            "read_only": False
        },
        {
            "id": 1316805,
            "table_id": 195388,
            "name": "Last name",
            "order": 1,
            "type": "text",
            "primary": False,
            "read_only": False
        },
        {
            "id": 1316806,
            "table_id": 195388,
            "name": "Notes",
            "order": 2,
            "type": "long_text",
            "primary": False,
            "read_only": False
        }
    ]

    mock_make_api_request.return_value = example_data

    baserow = Baserow()
    table = baserow.get_table(195388)
    fields = table.fields

    # Convert example_data to a list of Field objects
    expected_fields = FieldList([Field(data['name'], data) for data in example_data])

    # Assert that the two FieldLists contain equivalent Field objects
    assert len(fields) == len(expected_fields)
    for field, expected_field in zip(fields, expected_fields):
        assert field.name == expected_field.name
        assert field.field_data == expected_field.field_data

def test_fields_raises_error_on_api_failure(mock_make_api_request):
    mock_make_api_request.side_effect = Exception("API call failed!")

    baserow = Baserow()
    table = baserow.get_table(195388)

    with pytest.raises(Exception, match="Unexpected error when fetching fields."):
        fields = table.fields

    # Extract the actual arguments passed to the mock
    args, _ = mock_make_api_request.call_args

    # Check the 2nd argument directly (since we're ignoring the 1st argument)
    assert args[1] == f"/api/database/fields/table/{table.table_id}/"

def test_fields_does_not_refetch_when_already_set(mock_make_api_request):
    baserow = Baserow()
    table = baserow.get_table(195388)

    # Simulate a previous successful call
    table._fields = [{"name": "Previous", "type": "data"}]
    fields = table.fields

    # Check that mock_make_api_request was never called, implying fields were never refetched
    mock_make_api_request.assert_not_called()
    assert fields == [{"name": "Previous", "type": "data"}]

def test_get_field_names(mock_make_api_request):
    # Mocking the response from the API
    fields_data = [
        {
            "id": 1316804,
            "table_id": 195388,
            "name": "Name",
            "order": 0,
            "type": "text",
            "primary": True,
            "read_only": False
        },
        {
            "id": 1316805,
            "table_id": 195388,
            "name": "Last name",
            "order": 1,
            "type": "text",
            "primary": False,
            "read_only": False
        },
        {
            "id": 1316806,
            "table_id": 195388,
            "name": "Notes",
            "order": 2,
            "type": "long_text",
            "primary": False,
            "read_only": False
        }
    ]

    # Mock the `make_api_request` method to return the provided data
    mock_make_api_request.return_value = fields_data

    baserow = Baserow()
    table = baserow.get_table(195388)
    field_names = table.get_field_names()

    expected_field_names = ['Name', 'Last name', 'Notes']

    assert field_names == expected_field_names

def test_get_field_names_error_handling(mocker, mock_make_api_request, caplog):
    # Mocking the fields to raise an exception when accessed
    mock_table_fields = mocker.PropertyMock(side_effect=Exception("Sample error"))
    mocker.patch.object(Table, 'fields', mock_table_fields)

    baserow = Baserow()
    table = baserow.get_table(195388)

    with pytest.raises(Exception, match="Sample error"):
        field_names = table.get_field_names()

    # Check if the error was logged correctly
    assert f"Failed to get field names for table {table.table_id}. Error: Sample error" in caplog.text

def test_get_field_type_success(mock_make_api_request, mocker):
    sample_fields = [
        {"id": 1, "table_id": 195388, "name": "Name", "order": 0, "type": "text", "primary": True, "read_only": False},
        {"id": 2, "table_id": 195388, "name": "Last name", "order": 1, "type": "text", "primary": False, "read_only": False},
        {"id": 3, "table_id": 195388, "name": "Notes", "order": 2, "type": "long_text", "primary": False, "read_only": False}
    ]
    
    # Convert sample_fields to a FieldList of Field objects
    field_objects = FieldList([Field(data['name'], data) for data in sample_fields])

    baserow = Baserow()
    table = baserow.get_table(195388)

    # Mock the 'fields' property of the 'table' instance to return our FieldList
    mocker.patch.object(type(table), 'fields', new_callable=mocker.PropertyMock).return_value = field_objects
    
    assert table.get_field_type("Name") == "text"
    assert table.get_field_type("Last name") == "text"
    assert table.get_field_type("Notes") == "long_text"

def test_get_field_type_field_not_found(mock_make_api_request, mocker):
    sample_fields = [
        {"id": 1, "table_id": 195388, "name": "Name", "order": 0, "type": "text", "primary": True, "read_only": False},
    ]

    # Convert sample_fields to a FieldList of Field objects
    field_objects = FieldList([Field(data['name'], data) for data in sample_fields])

    baserow = Baserow()
    table = baserow.get_table(195388)

    # Mock the 'fields' property of the 'table' instance to return our FieldList
    mocker.patch.object(type(table), 'fields', new_callable=mocker.PropertyMock).return_value = field_objects
    
    with pytest.raises(ValueError, match="Field 'NonExistentField' not found in table 195388."):
        table.get_field_type("NonExistentField")

def test_get_row_success(mock_make_api_request):
    # Sample data for a successful row fetch
    row_sample_data = {
        "id": 123,
        "field_data": {
            "Name": "John",
            "Last name": "Doe",
            "Notes": "Sample Notes"
        }
    }

    # Mock the make_api_request method to return the above data
    mock_make_api_request.return_value = row_sample_data

    baserow = Baserow()
    table = baserow.get_table(195388)

    # Test the get_row method
    row = table.get_row(123)

    # Adjusted assertions
    assert row.fields == row_sample_data
    assert row.id == 123
    assert row.table == table
    assert row.client == baserow

    # Adjusted mock check
    mock_make_api_request.assert_called_once_with(baserow, f"/api/database/rows/table/{table.table_id}/123/?user_field_names=true")

def test_get_row_failure(mock_make_api_request):
    # Mock the make_api_request method to raise an exception
    mock_make_api_request.side_effect = Exception("Failed API call!")

    baserow = Baserow()
    table = baserow.get_table(195388)

    # Test the get_row method with pytest.raises to check for exceptions
    with pytest.raises(Exception, match="Failed API call!"):
        table.get_row(123)

    # Adjusted mock check
    mock_make_api_request.assert_called_once_with(baserow, f"/api/database/rows/table/{table.table_id}/123/?user_field_names=true")

# Sample data for tests
SINGLE_ROW_DATA = {"name": "John", "age": 28}
MULTIPLE_ROWS_DATA = [{"name": "John", "age": 28}, {"name": "Jane", "age": 25}]
API_RESPONSE_SINGLE = {"id": 1, "name": "John", "age": 28}
API_RESPONSE_MULTIPLE = {
    "items": [{"id": 1, "name": "John", "age": 28}, {"id": 2, "name": "Jane", "age": 25}]
}

@pytest.fixture
def mock_table(mocker):
    mocker.patch('baserowapi.models.table.FieldValidator.validate_fields_against_table')
    client = mocker.MagicMock()
    table = Table(client=client, table_id=12345)
    return table

def test_add_single_row(mock_table):
    mock_table.client.make_api_request.return_value = API_RESPONSE_SINGLE

    result_row = mock_table.add_row(SINGLE_ROW_DATA)
    
    mock_table.client.make_api_request.assert_called_once_with(
        "/api/database/rows/table/12345/?user_field_names=true", method="POST", data=SINGLE_ROW_DATA
    )
    assert result_row.fields == API_RESPONSE_SINGLE

def test_add_multiple_rows(mock_table):
    mock_table.client.make_api_request.return_value = API_RESPONSE_MULTIPLE

    result_rows = mock_table.add_row(MULTIPLE_ROWS_DATA)

    mock_table.client.make_api_request.assert_called_once_with(
        "/api/database/rows/table/12345/batch/?user_field_names=true", method="POST", data={'items': MULTIPLE_ROWS_DATA}
    )
    assert all(isinstance(row, Row) for row in result_rows)
    assert [row.fields for row in result_rows] == [row for row in API_RESPONSE_MULTIPLE['items']]

def test_add_row_field_validation_failure(mock_table, mocker):
    mock_table.client.make_api_request.return_value = API_RESPONSE_SINGLE
    
    # Use mocker to mock the FieldValidator method
    mock_validate = mocker.patch("baserowapi.validators.field_validator.FieldValidator.validate_fields_against_table")
    mock_validate.side_effect = Exception("Validation Error")

    with pytest.raises(Exception, match="Validation Error"):
        mock_table.add_row(SINGLE_ROW_DATA)

def test_add_row_api_request_failure(mock_table):
    mock_table.client.make_api_request.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="Failed to add row to table 12345. Error: API Error"):
        mock_table.add_row(SINGLE_ROW_DATA)

def test_primary_field_initialization(mocker):
    # Mock the API request for fields with sample data
    mocked_fields_data = [{"name": "name", "primary": True}, {"name": "age"}]

    # Mock the make_api_request method of Baserow
    mocker.patch.object(Baserow, 'make_api_request', return_value=mocked_fields_data)

    # Now create a Baserow object and get a table from it
    mock_baserow = Baserow(token='mock_token')  # A mock token is added just for the sake of completeness
    mock_table = mock_baserow.get_table(table_id=1)

    assert mock_table.primary_field == "name"

    # Test _set_primary_field
    mock_table._primary_field = None  # Resetting primary field for testing
    mock_table._set_primary_field()
    assert mock_table._primary_field == "name"

def test_no_primary_field_error(mocker):
    # Mock the API request for fields with data that does NOT include a primary field
    mocked_fields_data = [{"name": "name"}, {"name": "age"}]  # No field marked as primary

    # Mock the make_api_request method of Baserow
    mocker.patch.object(Baserow, 'make_api_request', return_value=mocked_fields_data)

    # Now create a Baserow object and get a table from it
    mock_baserow = Baserow(token='mock_token')  # A mock token for completeness
    mock_table = mock_baserow.get_table(table_id=1)

    # Now when you access mock_table.primary_field, it should raise a ValueError since there's no primary field
    with pytest.raises(ValueError, match=f"Table {mock_table.table_id} does not have a primary field."):
        _ = mock_table.primary_field

