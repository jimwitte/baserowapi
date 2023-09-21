import pytest
from baserowapi import Table

@pytest.fixture
def mock_table():
    # Enhanced MockTable with mock methods for 'make_api_request' and '_parse_row_data'
    class MockTable:
        def __init__(self):
            self.client = self._mock_client(self)
            self.responses = {
                "https://api.baserow.io/api/database/rows/table/195388/?user_field_names=true": {
                    "results": [{"id": 1, "name": "John"}, {"id": 2, "name": "Doe"}],
                    "next": "https://api.baserow.io/api/database/rows/table/195388/?page=2"
                },
                "https://api.baserow.io/api/database/rows/table/195388/?page=2": {
                    "results": [{"id": 3, "name": "Jane"}, {"id": 4, "name": "Smith"}],
                    "next": None
                },
                "https://api.baserow.io/api/database/rows/table/195388/?page=invalid": {"some_invalid_field": "some_value"}  # Invalid
            }

        class _mock_client:
            def __init__(self, outer_instance):
                self.outer_instance = outer_instance

            def make_api_request(self, url):
                return self.outer_instance.responses.get(url, {"results": [], "next": None})

        def _parse_row_data(self, response_data):
            return response_data.get('results', [])

    return MockTable()

def test_row_iterator_initialization(mock_table):
    initial_url = "https://api.baserow.io/api/database/rows/table/195388/?user_field_names=true"
    iterator = Table.RowIterator(table=mock_table, initial_url=initial_url)

    assert iterator.table == mock_table
    assert iterator.initial_url == initial_url
    assert iterator.next_page_url is None
    assert iterator.current_rows == []
    assert iterator.index == 0

def test_fetch_next_page_initial_url(mock_table):
    initial_url = "https://api.baserow.io/api/database/rows/table/195388/?user_field_names=true"
    row_iterator = Table.RowIterator(table=mock_table, initial_url=initial_url)
    
    first_row = next(row_iterator)
    assert first_row == {"id": 1, "name": "John"}
    
    second_row = next(row_iterator)
    assert second_row == {"id": 2, "name": "Doe"}

    # Check if next_page_url is set to the second page URL after iterating through the initial page.
    assert row_iterator.next_page_url == "https://api.baserow.io/api/database/rows/table/195388/?page=2"

def test_fetch_next_page_next_url(mock_table):
    initial_url = "https://api.baserow.io/api/database/rows/table/195388/?user_field_names=true"
    row_iterator = Table.RowIterator(table=mock_table, initial_url=initial_url)
    
    # Consume the first page
    next(row_iterator)
    next(row_iterator)

    # Now the rows from the second page should be fetched
    third_row = next(row_iterator)
    assert third_row == {"id": 3, "name": "Jane"}

    fourth_row = next(row_iterator)
    assert fourth_row == {"id": 4, "name": "Smith"}

    # After the fourth row, the iterator should be exhausted
    with pytest.raises(StopIteration):
        next(row_iterator)

def test_fetch_next_page_no_more_pages(mock_table):
    # Define the test initial_url
    initial_url = "https://api.baserow.io/api/database/rows/table/195388/?user_field_names=true"
    
    # Create the RowIterator instance
    iterator = Table.RowIterator(table=mock_table, initial_url=initial_url)

    # Manually force the fetching of all pages.
    rows_fetched = list(iterator)
    
    # At this point, we expect to have retrieved all rows across all pages.
    expected_rows = [{"id": 1, "name": "John"}, {"id": 2, "name": "Doe"}, {"id": 3, "name": "Jane"}, {"id": 4, "name": "Smith"}]
    assert rows_fetched == expected_rows

    # If we try to get another row, it should raise StopIteration.
    with pytest.raises(StopIteration):
        next(iterator)

def test_iteration_over_all_rows(mock_table):
    # Initial URL for the mock data
    initial_url = "https://api.baserow.io/api/database/rows/table/195388/?user_field_names=true"
    
    # Instantiate the RowIterator
    iterator = Table.RowIterator(table=mock_table, initial_url=initial_url)
    
    # Using list comprehension to get all rows from the iterator
    fetched_rows = [row for row in iterator]

    # Assert that all rows from the mock data are fetched
    expected_rows = [{"id": 1, "name": "John"}, {"id": 2, "name": "Doe"},
                     {"id": 3, "name": "Jane"}, {"id": 4, "name": "Smith"}]
    assert fetched_rows == expected_rows

def test_iteration_stops_at_end(mock_table):
    initial_url = "https://api.baserow.io/api/database/rows/table/195388/?user_field_names=true"
    iterator = Table.RowIterator(table=mock_table, initial_url=initial_url)

    # Expected rows collected from the mock responses
    expected_rows = [
        {"id": 1, "name": "John"},
        {"id": 2, "name": "Doe"},
        {"id": 3, "name": "Jane"},
        {"id": 4, "name": "Smith"},
    ]
    collected_rows = [row for row in iterator]

    # Assert the collected rows match the expected rows
    assert collected_rows == expected_rows

    # Try to get the next item from the iterator, expecting a StopIteration exception
    with pytest.raises(StopIteration):
        next(iterator)

def test_error_handling_on_data_fetch(mock_table):
    # Use the URL that has an invalid response in the mock table
    initial_url = "https://api.baserow.io/api/database/rows/table/195388/?page=invalid"
    iterator = Table.RowIterator(table=mock_table, initial_url=initial_url)

    # We expect the iterator to raise an exception when trying to fetch data from an invalid URL
    with pytest.raises(Exception, match="Error fetching next page of rows"):
        next(iterator)