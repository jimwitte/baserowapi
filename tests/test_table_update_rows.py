import pytest
from baserowapi.baserow import Baserow
from baserowapi.models.table import Table
from baserowapi.models.row import Row

@pytest.fixture
def mock_client(mocker):
    client = Baserow()
    mocker.patch.object(client, 'make_api_request', return_value={
        'items': [{'id': 1, 'order': '1.00000000000000000000', 'Name': 'updated_name'}]
    })
    return client

@pytest.fixture
def mock_table_without_rows(mock_client, mocker):
    # Mock Table without rows
    table = Table(client=mock_client, table_id=123)
    
    # Mock the fields property to return expected fields
    mocker.patch.object(Table, 'fields', return_value={"Name": {"name": "Name", "type": "text"}})
    
    return table

@pytest.fixture
def mock_row(mock_table_without_rows):
    row_data = {"id": 1, "order": 1, "Name": "test_name"}
    return Row(row_data=row_data, table=mock_table_without_rows, client=mock_table_without_rows.client)

@pytest.fixture
def mock_table_with_row(mock_table_without_rows, mock_row):
    # Add the mock_row to the table's rows
    mock_table_without_rows.rows = [mock_row]
    return mock_table_without_rows

def test_successful_update_of_rows(mock_table_with_row, mock_row, mocker):
    # Mocking the get_field_names method to return 'Name' as a valid field
    mock_table_with_row.get_field_names = mocker.MagicMock(return_value=["Name"])
    
    # Mock input rows data
    rows_data = [{"id": mock_row.id, "Name": "updated_name"}]

    # Call the update_rows method
    updated_rows = mock_table_with_row.update_rows(rows_data)

    # Validate updated rows
    assert len(updated_rows) == 1
    assert updated_rows[0].fields['Name'] == "updated_name"

def test_update_rows_with_rows(mock_table_with_row, mock_row, mocker):
    # Create another mock row for update
    updated_mock_row_data = {"id": mock_row.id, "order": 1, "Name": "updated_name"}
    updated_mock_row = Row(row_data=updated_mock_row_data, table=mock_table_with_row, client=mock_table_with_row.client)

    # Mocking the get_field_names method to return 'Name' as a valid field
    mock_table_with_row.get_field_names = mocker.MagicMock(return_value=["Name"])

    # Using Row objects for update
    rows_to_update = [updated_mock_row]

    # Call the update_rows method
    updated_rows = mock_table_with_row.update_rows(rows_to_update)

    # Validate updated rows
    assert len(updated_rows) == 1
    assert updated_rows[0].fields['Name'] == "updated_name"

def test_update_rows_with_mixed_input(mock_table_with_row, mock_row, mocker):
    # Mocking the get_field_names method to return 'Name' as a valid field
    mock_table_with_row.get_field_names = mocker.MagicMock(return_value=["Name"])

    # Create another mock row for update
    updated_mock_row_data = {"id": mock_row.id, "order": 1, "Name": "updated_row_name"}
    updated_mock_row = Row(row_data=updated_mock_row_data, table=mock_table_with_row, client=mock_table_with_row.client)

    # Mock the API response to return both updated rows
    mock_response = {'items': [updated_mock_row_data, {"id": mock_row.id, "Name": "updated_dict_name"}]}
    mocker.patch.object(mock_table_with_row.client, 'make_api_request', return_value=mock_response)

    # Mixed input: dictionary and Row object
    rows_to_update = [updated_mock_row, {"id": mock_row.id, "Name": "updated_dict_name"}]

    # Call the update_rows method
    updated_rows = mock_table_with_row.update_rows(rows_to_update)

    # Validate updated rows
    assert len(updated_rows) == 2
    # Check the first updated row
    assert updated_rows[0].fields['Name'] == "updated_row_name"
    # Check the second updated row
    assert updated_rows[1].fields['Name'] == "updated_dict_name"

def test_update_rows_with_empty_input(mock_table_with_row, mocker):
    # Mocking the get_field_names method to return 'Name' as a valid field
    mock_table_with_row.get_field_names = mocker.MagicMock(return_value=["Name"])
    
    # Mock the API response to return an empty list (though we expect it not to be called)
    mock_response = {'items': []}
    mocker.patch.object(mock_table_with_row.client, 'make_api_request', return_value=mock_response)

    # Call the update_rows method with an empty list
    with pytest.raises(ValueError, match="The rows_data list is empty. Nothing to update."):
        mock_table_with_row.update_rows([])

    # Ensure the API request was not made
    mock_table_with_row.client.make_api_request.assert_not_called()
