from .helper_functions.generate_identical_rows import generate_identical_rows

def test_create_row(all_fields_table, single_row_data):
    # Extract the input data, filtering out read-only fields
    input_data = {
        key: value["input"]
        for key, value in single_row_data.items()
        if not value["read_only"]
    }

    # Create a new row using the filtered input data
    new_row = all_fields_table.add_rows(input_data)[0]

    # Verify the data in the new row
    for field, value in single_row_data.items():
        if value["read_only"]:
            # If the field is read-only, just check that it exists in the returned data
            assert (
                field in new_row
            ), f"Field {field} should be present in the returned data."
        else:
            # If the field is not read-only, assert that the value matches the expected value
            assert (
                new_row[field] == value["expected"]
            ), f"Field {field} expected {value['expected']} but got {new_row[field]}"

    # Cleanup: Delete the row after the test
    all_fields_table.delete_rows([new_row.id])


def test_create_multiple_identical_rows(all_fields_table, single_row_data):
    # Generate identical data for 10 rows using the helper function
    multiple_rows_data = generate_identical_rows(single_row_data, num_rows=10)

    # Extract the input data for all rows, filtering out read-only fields
    input_data = [
        {key: value["input"] for key, value in row.items() if not value["read_only"]}
        for row in multiple_rows_data
    ]

    # Create multiple rows using the filtered input data
    created_rows = all_fields_table.add_rows(input_data)

    # Verify that the correct number of rows were created
    assert len(created_rows) == len(
        multiple_rows_data
    ), "Mismatch in number of rows created"

    # Verify the data in each created row
    for i, row in enumerate(multiple_rows_data):
        new_row = created_rows[i]
        for field, value in row.items():
            if value["read_only"]:
                # If the field is read-only, just check that it exists in the returned data
                assert (
                    field in new_row
                ), f"Field {field} should be present in the returned data for row {i+1}."
            else:
                # If the field is not read-only, assert that the value matches the expected value
                assert (
                    new_row[field] == value["expected"]
                ), f"Field {field} in row {i+1} expected {value['expected']} but got {new_row[field]}"

    # Cleanup: Delete all the rows after the test using the correct id attribute
    all_fields_table.delete_rows([row.id for row in created_rows])
