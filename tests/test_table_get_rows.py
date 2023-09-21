import pytest
from baserowapi import Baserow, Table, Row

@pytest.fixture
def mock_table():
    # Create an instance of the real Table class
    baserow_instance = Baserow()
    table = baserow_instance.get_table(123)
    
    responses = {
        "https://api.baserow.io/api/database/rows/table/123/?user_field_names=true": {
            "results": [{"id": 1, "name": "John"}, {"id": 2, "name": "Doe"}],
            "next": "https://api.baserow.io/api/database/rows/table/123/?page=2"
        },
        "https://api.baserow.io/api/database/rows/table/123/?page=2": {
            "results": [{"id": 3, "name": "Jane"}, {"id": 4, "name": "Smith"}],
            "next": None
        },
        "https://api.baserow.io/api/database/rows/table/123/?page=invalid": {
            "some_invalid_field": "some_value"  # Invalid response
        },
        "https://api.baserow.io/api/database/rows/table/123/?user_field_names=true&no_rows=true": {
            "results": [],
            "next": None
        },
        "https://api.baserow.io/api/database/rows/table/123/?user_field_names=true&error=true": {
            "error": "Failed to fetch row"
        }
    }

    class _mock_client:
        def __init__(self, outer_instance):
            self.outer_instance = outer_instance
            self.last_url = None

        def make_api_request(self, url):
            print("Setting last_url to:", url)
            self.last_url = url

            # if mock_url is set, use that
            if hasattr(self.outer_instance, 'mock_url') and self.outer_instance.mock_url:
                url = self.outer_instance.mock_url.replace('https://api.baserow.io', '')  # removing the base part to make it compatible with the logic

            base_url = "/api/database/rows/table/123/?user_field_names=true"
            if url == base_url:
                # Return a response depending on the has_rows attribute
                if self.outer_instance.has_rows:
                    response = self.outer_instance.responses["https://api.baserow.io/api/database/rows/table/123/?user_field_names=true"]
                else:
                    response = self.outer_instance.responses["https://api.baserow.io/api/database/rows/table/123/?user_field_names=true&no_rows=true"]
            else:
                full_url = "https://api.baserow.io" + url  # prepend the base URL
                response = self.outer_instance.responses.get(full_url, {"results": [], "next": None})
                
                # Check for an error response
                if "error" in response:
                    raise Exception(response["error"])

            return response

    # Replace the table's client with the mock client
    table.client = _mock_client(table)
    table.responses = responses
    
    # By default, the mock table should have rows
    table.has_rows = True

    return table


@pytest.fixture
def mock_valid_request_url():
    # You can adjust this URL based on the API's actual behavior.
    return "https://api.baserow.io/api/database/rows/table/195388/?user_field_names=true"

@pytest.fixture
def mock_response_data():
    return {
        "results": [{"id": 1, "name": "John"}, {"id": 2, "name": "Doe"}, {"id": 3, "name": "Jane"}],
        "next": None
    }

@pytest.fixture
def mock_client(mock_response_data):
    class MockClient:
        def make_api_request(self, url):
            # This mimics the behavior of the client making a request and getting a response.
            return mock_response_data
    return MockClient()

def test_get_rows_valid_parameters(mock_table, mock_valid_request_url, mock_client):
    # Inject the mock client into the table instance
    mock_table.client = mock_client
    
    # Call the get_rows function
    rows_iterator = mock_table.get_rows()  # No parameters here as we're testing default behavior

    # Now, we can make a few assertions
    assert isinstance(rows_iterator, Table.RowIterator), "Expected a RowIterator object"
    
    # If you wish to assert the data, convert the iterator to a list and check the row data.
    rows = list(rows_iterator)
    assert len(rows) == 3
    assert rows[0]['name'] == "John"
    assert rows[1]['name'] == "Doe"
    assert rows[2]['name'] == "Jane"


def test_get_rows_invalid_parameters(mock_table):
    # 1. Pass a non-existent filter type
    with pytest.raises(Exception, match="Invalid parameters"):
        mock_table.get_rows(filter_type="NON_EXISTENT_FILTER")

    # 2. Pass an invalid view ID format (string instead of int)
    with pytest.raises(Exception, match="Invalid parameters"):
        mock_table.get_rows(view_id="some_string_instead_of_int")

    # 3. Pass an invalid include format (number instead of string)
    with pytest.raises(Exception, match="Invalid parameters"):
        mock_table.get_rows(include=123456)

    # 4. Pass an invalid exclude format (number instead of string)
    with pytest.raises(Exception, match="Invalid parameters"):
        mock_table.get_rows(exclude=123456)

    # 5. Pass an invalid search format (number instead of string)
    with pytest.raises(Exception, match="Invalid parameters"):
        mock_table.get_rows(search=123456)

    # 6. Pass an invalid order_by format (number instead of string)
    with pytest.raises(Exception, match="Invalid parameters"):
        mock_table.get_rows(order_by=123456)

    # 7. Pass an invalid page_size format (string instead of int)
    with pytest.raises(Exception, match="Invalid parameters"):
        mock_table.get_rows(page_size="some_string_instead_of_int")

def test_get_rows_with_return_single_true_and_rows_exist(mock_table):
    # Fetch a single row with return_single=True
    row = mock_table.get_rows(return_single=True)

    # Check that the result is a Row instance
    assert isinstance(row, Row), "Expected a Row object"

    # Check that the returned Row object has valid attributes
    assert hasattr(row, 'id'), "Expected the Row object to have an 'id' attribute"
    assert hasattr(row, 'order'), "Expected the Row object to have an 'order' attribute"
    assert hasattr(row, 'fields'), "Expected the Row object to have a 'fields' attribute"
    assert row.id in [1, 2, 3, 4], "Expected the Row object id to be one of the mock data ids"

def test_get_rows_with_return_single_true_and_no_rows(mock_table):
    # Simulate the condition where the table has no rows
    mock_table.has_rows = False

    # Fetch a single row with return_single=True
    row = mock_table.get_rows(return_single=True)
    
    # Check that the result is None as there are no rows
    assert row is None, "Expected None when there are no rows and return_single=True"


def test_get_rows_error_fetching_single_row(mock_table):
    # Set the mock URL to simulate an error
    mock_table.mock_url = "https://api.baserow.io/api/database/rows/table/123/?user_field_names=true&error=true"
    
    # Try to fetch a single row and expect an error
    with pytest.raises(Exception, match="Failed to fetch row"):
        row = mock_table.get_rows(return_single=True)

