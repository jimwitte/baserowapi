import pytest
from baserowapi.exceptions import (
    RowFetchError,
)


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
