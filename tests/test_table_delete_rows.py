import pytest
from baserowapi.baserow import Baserow
from baserowapi.models.table import Table
from baserowapi.models.row import Row

# Fixtures

@pytest.fixture
def mock_client(mocker):
    client = Baserow()
    mocker.patch.object(client, 'make_api_request', return_value=204)  # Assuming 204 is the status for successful deletion.
    return client

@pytest.fixture
def mock_table(mock_client):
    return Table(client=mock_client, table_id=123)

@pytest.fixture
def mock_row(mock_table):
    row_data = {"id": 1, "order": 1, "Name": "test_name"}
    return Row(row_data=row_data, table=mock_table, client=mock_table.client)

# Tests

def test_delete_rows_with_row_objects(mock_table, mock_row, mocker):
    # Mock the rows to be deleted
    rows_to_delete = [mock_row]

    # Call the delete_rows method
    response_status = mock_table.delete_rows(rows_to_delete)

    # Validate deletion response
    assert response_status == 204

def test_delete_rows_with_dicts(mock_table, mocker):
    # Mock the rows data to be deleted as dicts
    rows_data_to_delete = [{"id": 1}]

    # Call the delete_rows method
    response_status = mock_table.delete_rows(rows_data_to_delete)

    # Validate deletion response
    assert response_status == 204

def test_delete_rows_with_mixed_input(mock_table, mock_row, mocker):
    # Mock mixed rows data (Row objects and dicts)
    rows_data_to_delete = [mock_row, {"id": 2}]

    # Call the delete_rows method
    response_status = mock_table.delete_rows(rows_data_to_delete)

    # Validate deletion response
    assert response_status == 204

def test_delete_rows_with_invalid_input(mock_table, mocker):
    # Mock invalid rows data
    rows_data_to_delete = [1, "string", {"name": "test_name"}]  # Invalid inputs

    with pytest.raises(TypeError):
        mock_table.delete_rows(rows_data_to_delete)

def test_delete_rows_with_empty_input(mock_table, mocker):
    # Mock empty rows data
    rows_data_to_delete = []

    with pytest.raises(ValueError):
        mock_table.delete_rows(rows_data_to_delete)
