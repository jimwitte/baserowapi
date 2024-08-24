import pytest
from baserowapi.exceptions import RowFetchError

def test_get_row_by_id(all_fields_table, single_row_data):
    
    # Step 1: Create a row
    input_data = {
        key: value["input"] for key, value in single_row_data.items() if not value["read_only"]
    }
    created_row = all_fields_table.add_rows(input_data)[0]

    # Step 2: Fetch the row by its ID
    fetched_row = all_fields_table.get_row(created_row.id)

    # Step 3: Verify that the fetched row matches the created row's data
    for field, value in single_row_data.items():
        if not value["read_only"]:
            assert fetched_row[field] == value["expected"], f"Field {field} does not match expected value."
    
    # Step 4: Clean up by deleting the row
    all_fields_table.delete_rows([created_row.id])


def test_get_non_existent_row_raises_error(all_fields_table):
    # Step 1: Define a non-existent row ID (e.g., a large number unlikely to be in the table)
    non_existent_row_id = 999999

    # Step 2: Attempt to fetch the row and expect a RowFetchError
    with pytest.raises(RowFetchError):
        all_fields_table.get_row(non_existent_row_id)


def test_get_row_with_invalid_id_type(all_fields_table):
    # Test with a non-integer ID (e.g., a string)
    invalid_row_id = "invalid_id"

    with pytest.raises(ValueError):
        all_fields_table.get_row(invalid_row_id)

    # Test with a None ID
    with pytest.raises(ValueError):
        all_fields_table.get_row(None)

def test_get_row_with_boundary_ids(all_fields_table):
    # Test with row ID 0
    with pytest.raises(ValueError):
        all_fields_table.get_row(0)

    # Test with a negative row ID
    with pytest.raises(RowFetchError):
        all_fields_table.get_row(-1)