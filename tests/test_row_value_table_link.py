import pytest

def test_table_link_field_get_options(all_fields_table):
    # Step 1: Access the TableLink field
    table_link_field = all_fields_table.fields['TableLink']

    # Step 2: Get options from the linked table
    linked_values = table_link_field.get_options()

    # Step 3: Verify that the returned list matches the expected values
    expected_values = ['fred', 'neil', 'geddy', 'alex']
    assert linked_values == expected_values, (
        f"Expected {expected_values}, but got {linked_values}"
    )


def test_update_table_link_row_value(all_fields_table):
    # Step 1: Create a row with initial data
    single_row_data = {
        "Name": "Test Row",
        "TableLink": []
    }
    created_row = all_fields_table.add_rows([single_row_data])[0]

    # Step 2: Query the options available for the TableLink field
    table_link_field = all_fields_table.fields['TableLink']
    available_options = table_link_field.get_options()

    # Verify that there are enough options to proceed
    assert len(available_options) >= 2, "Not enough options available in the linked table."

    # Step 3: Build an update value list with two of the options
    update_value_list = available_options[:2]  # Select the first two options

    # Step 4: Set the TableLink field to the new update value list
    created_row.values['TableLink'].value = update_value_list

    # Step 5: Update the row on the server
    created_row.update()

    # Step 6: Fetch the row by ID to verify the update
    updated_row = all_fields_table.get_row(created_row.id)

    # Step 7: Verify that the new value is the expected value
    assert updated_row['TableLink'] == update_value_list, (
        f"Expected TableLink value {update_value_list}, but got {updated_row['TableLink']}"
    )

    # Step 8: Clean up by deleting the row
    all_fields_table.delete_rows([created_row.id])