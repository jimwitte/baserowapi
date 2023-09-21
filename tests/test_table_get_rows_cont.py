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
            print("Setting last_url to None in init")
            self.last_url = None

        def make_api_request(self, url):
            print("Setting last_url in mock make_api_request to:", url)
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
                
            print(f"Response from mock make_api_request: {response}")
            return response

    # Replace the table's client with the mock client
    table.client = _mock_client(table)
    table.responses = responses
    
    # By default, the mock table should have rows
    table.has_rows = True

    return table

def test_get_rows_with_page_size(mock_table):
    # Given a specific PAGE_SIZE
    PAGE_SIZE = 10

    # When we call the get_rows method with the PAGE_SIZE. Need to iterate over rows
    rows = list(mock_table.get_rows(page_size=PAGE_SIZE))

    # The expected URL should include the page_size parameter
    expected_url = "/api/database/rows/table/123/?user_field_names=true&page_size=10"
    assert mock_table.client.last_url == expected_url, f"Expected URL to be {expected_url}, but got {mock_table.client.last_url}."
