import pytest
from .helper_functions.generate_identical_rows import generate_identical_rows

pytestmark = pytest.mark.integration


def test_update_single_row(all_fields_table, single_row_data):
    # Step 1: Create a single row
    input_data = {
        key: value["input"] for key, value in single_row_data.items() if not value["read_only"]
    }
    created_row = all_fields_table.add_row(input_data)

    # Step 2: Prepare update data
    update_data = {
        "Name": "Updated Name",
        "Notes": "Updated note for testing",
        "Active": False,
        "Number": 84,
    }

    # Step 3: Update the row with the new data
    created_row.update(update_data)

    # Step 4: Fetch the updated row to verify the update
    updated_row = all_fields_table.get_row(created_row.id)

    # Step 5: Verify that the row was updated correctly
    assert updated_row["Name"] == "Updated Name", "Name was not updated correctly."
    assert updated_row["Notes"] == "Updated note for testing", "Notes were not updated correctly."
    assert updated_row["Active"] is False, "Active status was not updated correctly."
    assert updated_row["Number"] == "84.00", "Number was not updated correctly."

def test_update_single_row_requires_explicit_values(all_fields_table, single_row_data):
    # Step 1: Create a single row
    input_data = {
        key: value["input"] for key, value in single_row_data.items() if not value["read_only"]
    }
    created_row = all_fields_table.add_row(input_data)

    # Step 2: Update explicitly; Row has no staged mutable state.
    created_row.update({
        'Name': 'Updated Name',
        'Notes': 'Updated note for testing',
        'Active': False,
        'Number': 84,
    })

    # Step 4: Fetch the updated row to verify the update
    updated_row = all_fields_table.get_row(created_row.id)

    # Step 5: Verify that the row was updated correctly
    assert updated_row['Name'] == 'Updated Name', 'Name was not updated correctly.'
    assert updated_row['Notes'] == 'Updated note for testing', 'Notes were not updated correctly.'
    assert updated_row['Active'] is False, 'Active status was not updated correctly.'
    assert updated_row['Number'] == '84.00', 'Number was not updated correctly.'

def test_delete_single_row(all_fields_table, single_row_data):
    # Step 1: Create multiple rows
    multiple_rows_data = generate_identical_rows(single_row_data, num_rows=3)
    input_data = [
        {key: value["input"] for key, value in row.items() if not value["read_only"]}
        for row in multiple_rows_data
    ]
    created_rows = all_fields_table.add_rows(input_data)

    # Step 2: Delete one of the rows
    row_to_delete = created_rows[1]
    row_to_delete_id = row_to_delete.id
    row_to_delete.delete()

    # Step 3: Fetch all rows to verify the deletion
    remaining_rows = all_fields_table.get_rows()

    # Step 4: Verify that the deleted row is no longer present
    remaining_row_ids = {row.id for row in remaining_rows}
    assert row_to_delete_id not in remaining_row_ids, f"Row with ID {row_to_delete_id} was not deleted."

def test_move_row_to_last_position(all_fields_table, single_row_data):
    # Step 1: Create multiple rows
    multiple_rows_data = generate_identical_rows(single_row_data, num_rows=3)
    input_data = [
        {key: value["input"] for key, value in row.items() if not value["read_only"]}
        for row in multiple_rows_data
    ]
    created_rows = all_fields_table.add_rows(input_data)

    # Step 2: Move the second row to the last position
    row_to_move = created_rows[1]
    row_to_move_id = row_to_move.id
    row_to_move.move()

    # Step 3: Fetch all rows to verify the move
    all_rows = all_fields_table.get_rows()

    # Step 4: Verify that the moved row is now the last row
    last_row_id = all_rows[-1].id
    assert last_row_id == row_to_move_id, f"Expected row ID {row_to_move_id} to be last, but got {last_row_id}."

def test_move_row_before_another_row(all_fields_table, single_row_data):
    # Step 1: Create multiple rows
    multiple_rows_data = generate_identical_rows(single_row_data, num_rows=4)
    input_data = [
        {key: value["input"] for key, value in row.items() if not value["read_only"]}
        for row in multiple_rows_data
    ]
    created_rows = all_fields_table.add_rows(input_data)

    # Step 2: Note the ID of the row that will be used as before_row_id
    before_row = created_rows[2]  # The row before which we will move another row
    before_row_id = before_row.id

    # Step 3: Move the first row to before the before_row
    row_to_move = created_rows[0]
    row_to_move_id = row_to_move.id
    row_to_move.move(before_id=before_row_id)

    # Step 4: Fetch all rows to verify the move
    all_rows = all_fields_table.get_rows()

    # Step 5: Verify that the moved row is now correctly positioned
    row_ids_in_order = [row.id for row in all_rows]
    expected_order = [created_rows[1].id, row_to_move_id, before_row_id, created_rows[3].id]

    assert row_ids_in_order == expected_order, (
        f"Expected order of rows: {expected_order}, but got: {row_ids_in_order}"
    )
