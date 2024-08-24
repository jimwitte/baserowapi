import pytest
from baserowapi.exceptions import (
    RowFetchError,
)
from .helper_functions.generate_identical_rows import generate_identical_rows


def test_delete_row(all_fields_table, single_row_data):
    # Create a row to delete
    input_data = {
        key: value["input"]
        for key, value in single_row_data.items()
        if not value["read_only"]
    }
    new_row = all_fields_table.add_rows(input_data)[0]

    # Delete the row
    all_fields_table.delete_rows([new_row.id])

    # Attempt to fetch the deleted row
    with pytest.raises(RowFetchError):
        all_fields_table.get_row(new_row.id)


def test_delete_multiple_rows(all_fields_table, single_row_data):
    # Generate data for multiple rows
    multiple_rows_data = generate_identical_rows(single_row_data, num_rows=5)

    # Create multiple rows using the filtered input data
    input_data = [
        {key: value["input"] for key, value in row.items() if not value["read_only"]}
        for row in multiple_rows_data
    ]
    created_rows = all_fields_table.add_rows(input_data)

    # Delete all rows
    all_fields_table.delete_rows([row.id for row in created_rows])

    # Attempt to fetch each deleted row and verify that RowFetchError is raised
    for row in created_rows:
        with pytest.raises(RowFetchError):
            all_fields_table.get_row(row.id)