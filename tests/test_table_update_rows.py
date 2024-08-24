import pytest
from baserowapi.exceptions import (
    RowDeleteError,
)
from .helper_functions.generate_identical_rows import generate_identical_rows


def test_update_row(all_fields_table, single_row_data):
    # Create a row to update
    input_data = {
        key: value["input"]
        for key, value in single_row_data.items()
        if not value["read_only"]
    }
    new_row = all_fields_table.add_rows(input_data)[0]

    # Prepare updated data (e.g., change the 'Name' and 'Notes' fields)
    updated_data = {
        "Name": "Updated Test Name",
        "Notes": "Updated sample note for testing",
    }

    # Update the row with new data
    new_row.update(updated_data)

    # Fetch the row again to verify the update
    updated_row = all_fields_table.get_row(new_row.id)

    assert (
        updated_row["Name"] == "Updated Test Name"
    ), "Name field was not updated correctly."
    assert (
        updated_row["Notes"] == "Updated sample note for testing"
    ), "Notes field was not updated correctly."

    # Clean up by deleting the row
    all_fields_table.delete_rows([new_row.id])


def test_update_multiple_rows(all_fields_table, single_row_data):
    # Generate data for multiple rows
    multiple_rows_data = generate_identical_rows(single_row_data, num_rows=5)

    # Create multiple rows using the filtered input data
    input_data = [
        {key: value["input"] for key, value in row.items() if not value["read_only"]}
        for row in multiple_rows_data
    ]
    created_rows = all_fields_table.add_rows(input_data)

    # Prepare updated data to be applied to all rows (e.g., change the 'Active' and 'Notes' fields)
    updated_data = {
        "Active": False,
        "Notes": "Bulk update note"
    }

    # Update all rows with new data
    for row in created_rows:
        row.update(updated_data)

    # Fetch and verify the updated rows
    for row in created_rows:
        updated_row = all_fields_table.get_row(row.id)
        assert updated_row["Active"] is False, "Active field was not updated correctly."
        assert updated_row["Notes"] == "Bulk update note", "Notes field was not updated correctly."

    # Clean up by deleting the rows that still exist
    remaining_row_ids = [row.id for row in created_rows]
    if remaining_row_ids:
        all_fields_table.delete_rows(remaining_row_ids)


def test_update_and_delete_with_missing_rows(all_fields_table, single_row_data):
    # Generate data for multiple rows
    multiple_rows_data = generate_identical_rows(single_row_data, num_rows=5)

    # Create multiple rows using the filtered input data
    input_data = [
        {key: value["input"] for key, value in row.items() if not value["read_only"]}
        for row in multiple_rows_data
    ]
    created_rows = all_fields_table.add_rows(input_data)

    # Delete a few rows to simulate missing rows
    rows_to_delete = created_rows[:2]
    all_fields_table.delete_rows([row.id for row in rows_to_delete])

    # Attempt to update all remaining rows
    updated_data = {
        "Active": False,
        "Notes": "Update note after deletion"
    }

    for row in created_rows:
        if row not in rows_to_delete:
            row.update(updated_data)
            updated_row = all_fields_table.get_row(row.id)
            assert updated_row["Active"] is False, "Active field was not updated correctly."
            assert updated_row["Notes"] == "Update note after deletion", "Notes field was not updated correctly."

    # Cleanup: Delete only the remaining rows
    rows_remaining = [row.id for row in created_rows if row not in rows_to_delete]
    if rows_remaining:
        all_fields_table.delete_rows(rows_remaining)