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
