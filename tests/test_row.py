import pytest
from baserowapi.models.row import Row
from baserowapi.models.table import Table
from baserowapi.validators.field_validator import FieldValidator
import logging

# Fixture for the mock Baserow client
@pytest.fixture
def mock_client():
    class MockClient:
        def make_api_request(self, endpoint, method="GET", data=None):
            return {}
    
    return MockClient()

# Fixture for the mock Table object
@pytest.fixture
def mock_table(mock_client):
    class MockTable:
        def __init__(self):
            self.table_id = "sample_table_id"
    
    return MockTable()

def test_row_initialization_with_given_data(mock_table, mock_client):
    # Sample row data for testing
    row_data = {
        'id': 'sample_id',
        'order': 'sample_order',
        'field1': 'value1',
        'field2': 'value2'
    }

    # Initialize the Row object
    row = Row(row_data=row_data, table=mock_table, client=mock_client)

    # Assertions
    assert row.id == row_data['id']
    assert row.order == row_data['order']
    assert row.fields == row_data
    assert row.table_id == mock_table.table_id

def test_row_table_id_is_correctly_set_from_table_object(mock_table, mock_client):
    # Sample row data for testing
    row_data = {
        'id': 'sample_id',
        'order': 'sample_order',
        'field1': 'value1',
        'field2': 'value2'
    }

    # Initialize the Row object
    row = Row(row_data=row_data, table=mock_table, client=mock_client)

    # Assertion
    assert row.table_id == mock_table.table_id, f"Expected table_id to be {mock_table.table_id}, but got {row.table_id}."

# Continue from the previous code ...

def test_row_repr_method(mock_table, mock_client):
    # Sample row data for testing
    row_data = {
        'id': 'sample_id',
        'order': 'sample_order',
        'field1': 'value1',
        'field2': 'value2'
    }

    # Initialize the Row object
    row = Row(row_data=row_data, table=mock_table, client=mock_client)

    # Expected representation
    expected_repr = f"Row id {row_data['id']} of table {mock_table.table_id}"

    # Assertion
    assert str(row) == expected_repr, f"Expected repr to be {expected_repr}, but got {str(row)}."


@pytest.fixture
def sample_row_data():
    return {'id': 'sample_id', 'order': 'sample_order', 'field1': 'value1'}

@pytest.fixture
def sample_row(mock_table, mock_client, sample_row_data):
    return Row(table=mock_table, client=mock_client, row_data=sample_row_data)

def test_getitem_method(sample_row):
    assert sample_row['field1'] == 'value1'

def test_getitem_method_non_existent_field(caplog, sample_row):
    with caplog.at_level(logging.WARNING):
        value = sample_row['non_existent_field']
    assert "Field 'non_existent_field' not found in row." in caplog.text

def test_setitem_method(sample_row):
    sample_row['field1'] = 'new_value'
    assert sample_row['field1'] == 'new_value'

def test_setitem_method_new_field(caplog, sample_row):
    with caplog.at_level(logging.WARNING):
        sample_row['new_field'] = 'new_value'
    assert "Setting new field 'new_field' in row. Consider checking field validity." in caplog.text

def test_update_fields_correctly_updates_fields(sample_row):
    update_data = {'field1': 'updated_value'}
    sample_row.update_fields(update_data)
    assert sample_row['field1'] == 'updated_value'

def test_update_fields_raises_valueerror_for_non_existent_fields(sample_row):
    update_data = {'non_existent_field': 'some_value'}
    with pytest.raises(ValueError, match="Field 'non_existent_field' does not exist in the current row."):
        sample_row.update_fields(update_data)

# Extend the mock_client to include a method to mock the API request
@pytest.fixture
def mock_client_with_update_request(mocker):
    class _mock_client:
        def __init__(self):
            self.should_fail = False
            
        def make_api_request(self, *args, **kwargs):
            if self.should_fail:
                raise Exception("API request failed.")
            else:
                return {'id': 'sample_id', 'order': 'sample_order', 'field1': 'updated_value'}
    return _mock_client()


def test_update_method_successfully_sends_request_and_returns_updated_row(mock_client_with_update_request, mocker, sample_row):
    sample_row.client = mock_client_with_update_request
    mocker.patch.object(FieldValidator, 'validate_fields_against_table')
    updated_row = sample_row.update({'field1': 'updated_value'})
    assert updated_row['field1'] == 'updated_value'


def test_update_method_correctly_validates_fields_against_table_schema(mocker, sample_row):
    # Mock to check if validate_fields_against_table is called
    mock_validate = mocker.patch.object(FieldValidator, 'validate_fields_against_table')
    sample_row.update({'field1': 'updated_value'})
    mock_validate.assert_called_once()

def test_update_method_logs_error_and_raises_exception_on_failed_api_request(mock_client_with_update_request, mocker, sample_row, caplog):
    # Setting up the client to fail
    mock_client_with_update_request.should_fail = True

    sample_row.client = mock_client_with_update_request

    # Mocking the FieldValidator to avoid unwanted calls
    mocker.patch.object(FieldValidator, 'validate_fields_against_table')

    # Checking if an error is logged and an exception is raised
    with caplog.at_level(logging.ERROR):
        with pytest.raises(Exception, match="API request failed."):
            sample_row.update({'field1': 'updated_value'})
    
    assert "API request failed." in caplog.text


# Extend the mock_client to include a method to mock the DELETE API request
@pytest.fixture
def mock_client_with_delete_request(mocker):
    class _mock_client:
        def __init__(self):
            self.should_fail = False

        def make_api_request(self, endpoint, method="GET", data=None):
            if method == "DELETE":
                if self.should_fail:
                    raise Exception("API delete request failed.")
                else:
                    return 204  # Simulating a 204 No Content response for successful delete
            else:
                return {'id': 'sample_id', 'order': 'sample_order', 'field1': 'updated_value'}
    return _mock_client()

def test_delete_method_successfully_sends_delete_request(mock_client_with_delete_request, sample_row):
    sample_row.client = mock_client_with_delete_request
    result = sample_row.delete()
    assert result == 204

def test_delete_method_logs_error_and_raises_exception_on_failed_api_request(mock_client_with_delete_request, sample_row, caplog):
    # Setting up the client to fail
    mock_client_with_delete_request.should_fail = True
    sample_row.client = mock_client_with_delete_request

    # Checking if an error is logged and an exception is raised
    with caplog.at_level(logging.ERROR):
        with pytest.raises(Exception, match="API delete request failed."):
            sample_row.delete()
    
    assert "Failed to delete row with ID sample_id from table sample_table_id. Error: API delete request failed." in caplog.text
