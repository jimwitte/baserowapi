import pytest
from baserowapi import Filter


from .helper_functions.generate_identical_rows import generate_identical_rows

def test_get_all_rows(all_fields_table, single_row_data):
    # Step 1: Generate data for multiple rows
    num_rows = 5  # Create 5 rows for this test
    multiple_rows_data = generate_identical_rows(single_row_data, num_rows=num_rows)

    # Step 2: Create multiple rows using the generated data
    created_rows = all_fields_table.add_rows([
        {key: value["input"] for key, value in row.items() if not value["read_only"]}
        for row in multiple_rows_data
    ])
    created_row_ids = [row.id for row in created_rows]

    # Step 3: Fetch all rows using get_rows() with no parameters
    fetched_rows = all_fields_table.get_rows()

    # Step 4: Verify that all created rows are returned
    assert len(fetched_rows) == num_rows, f"Expected {num_rows} rows, but got {len(fetched_rows)}"

    # Verify that each created row is in the fetched results
    fetched_row_ids = [row.id for row in fetched_rows]
    for row_id in created_row_ids:
        assert row_id in fetched_row_ids, f"Row with ID {row_id} was not returned by get_rows()."

    # Step 5: Clean up by deleting the rows
    all_fields_table.delete_rows(created_row_ids)

def test_get_rows_empty_table(all_fields_table):
    # Step 1: Ensure the table is empty by fetching all rows
    fetched_rows = all_fields_table.get_rows()

    # Step 2: Verify that the returned list is empty
    assert fetched_rows == [], f"Expected an empty list, but got {fetched_rows}"

    # No cleanup necessary since the table is empty

def test_get_rows_with_include_fields(all_fields_table, single_row_data):
    # Step 1: Generate data for multiple rows
    num_rows = 3  # Create 3 rows for this test
    multiple_rows_data = generate_identical_rows(single_row_data, num_rows=num_rows)

    # Step 2: Create multiple rows using the generated data
    created_rows = all_fields_table.add_rows([
        {key: value["input"] for key, value in row.items() if not value["read_only"]}
        for row in multiple_rows_data
    ])
    created_row_ids = [row.id for row in created_rows]

    # Step 3: Fetch rows with the 'include' parameter (e.g., 'Name' and 'Active')
    fetched_rows = all_fields_table.get_rows(include=['Name', 'Active'])

    # Step 4: Verify that only the included fields are returned
    for row in fetched_rows:
        assert row.values.fields == ['Name', 'Active'], f"Expected fields ['Name', 'Active'], but got {row.values.fields}"

    # Step 5: Clean up by deleting the rows
    all_fields_table.delete_rows(created_row_ids)


def test_get_rows_with_exclude_fields(all_fields_table, single_row_data):
    # Step 1: Generate data for multiple rows
    num_rows = 3  # Create 3 rows for this test
    multiple_rows_data = generate_identical_rows(single_row_data, num_rows=num_rows)

    # Step 2: Create multiple rows using the generated data
    created_rows = all_fields_table.add_rows([
        {key: value["input"] for key, value in row.items() if not value["read_only"]}
        for row in multiple_rows_data
    ])
    created_row_ids = [row.id for row in created_rows]

    # Step 3: Fetch rows with the 'exclude' parameter (e.g., 'Name' and 'Active')
    fetched_rows = all_fields_table.get_rows(exclude=['Name', 'Active'])

    # Step 4: Verify that the excluded fields are not in the results
    for row in fetched_rows:
        assert 'Name' not in row.values.fields, "Field 'Name' should not be included in the results"
        assert 'Active' not in row.values.fields, "Field 'Active' should not be included in the results"

    # Step 5: Clean up by deleting the rows
    all_fields_table.delete_rows(created_row_ids)


def test_get_rows_with_limit(all_fields_table, single_row_data):
    # Step 1: Generate data for multiple rows
    num_rows = 5  # Create 5 rows for this test
    multiple_rows_data = generate_identical_rows(single_row_data, num_rows=num_rows)

    # Step 2: Create multiple rows using the generated data
    created_rows = all_fields_table.add_rows([
        {key: value["input"] for key, value in row.items() if not value["read_only"]}
        for row in multiple_rows_data
    ])
    created_row_ids = [row.id for row in created_rows]

    # Step 3: Fetch rows with the 'limit' parameter (e.g., limit=1)
    limited_rows = all_fields_table.get_rows(limit=1)

    # Step 4: Verify that only the limited number of rows are returned
    assert len(limited_rows) == 1, f"Expected 1 row, but got {len(limited_rows)}"

    # Step 5: Clean up by deleting the rows
    all_fields_table.delete_rows(created_row_ids)


def test_get_rows_with_search(all_fields_table, single_row_data):
    # Step 1: Generate data for multiple rows
    num_rows = 4  # Create 4 rows for this test
    multiple_rows_data = generate_identical_rows(single_row_data, num_rows=num_rows)

    # Modify the "Notes" field for each row to create varying content
    multiple_rows_data[0]["Notes"]["input"] = "Sample note for testing 1"
    multiple_rows_data[1]["Notes"]["input"] = "Sample note for testing 2"
    multiple_rows_data[2]["Notes"]["input"] = "Different content in notes"
    multiple_rows_data[3]["Notes"]["input"] = "Sample note for testing 3"

    # Step 2: Create multiple rows using the generated data
    created_rows = all_fields_table.add_rows([
        {key: value["input"] for key, value in row.items() if not value["read_only"]}
        for row in multiple_rows_data
    ])
    created_row_ids = [row.id for row in created_rows]

    # Step 3: Fetch rows with the 'search' parameter
    search_text = "Sample note for testing"
    search_results = all_fields_table.get_rows(search=search_text)

    # Step 4: Verify that only rows with the search text in the "Notes" column are returned
    assert len(search_results) == 3, f"Expected 3 rows, but got {len(search_results)}"

    for row in search_results:
        assert search_text in row["Notes"], f"Search text '{search_text}' not found in Notes for row {row.id}"

    # Step 5: Clean up by deleting the rows
    all_fields_table.delete_rows(created_row_ids)


def test_get_rows_with_order_by(all_fields_table, single_row_data):
    # Step 1: Generate data for multiple rows with custom "Name" and "Notes" content
    multiple_rows_data = generate_identical_rows(single_row_data, num_rows=4)
    
    # Customizing row data for sorting test
    multiple_rows_data[0]["Name"]["input"] = "Alice"
    multiple_rows_data[0]["Notes"]["input"] = "Note B"
    
    multiple_rows_data[1]["Name"]["input"] = "Bob"
    multiple_rows_data[1]["Notes"]["input"] = "Note A"
    
    multiple_rows_data[2]["Name"]["input"] = "Alice"
    multiple_rows_data[2]["Notes"]["input"] = "Note A"
    
    multiple_rows_data[3]["Name"]["input"] = "Bob"
    multiple_rows_data[3]["Notes"]["input"] = "Note B"

    # Step 2: Create the rows
    input_data = [
        {key: value["input"] for key, value in row.items() if not value["read_only"]}
        for row in multiple_rows_data
    ]
    created_rows = all_fields_table.add_rows(input_data)
    
    # Step 3: Fetch rows with ordering by "Name" ascending then "Notes" ascending
    ordered_rows = all_fields_table.get_rows(order_by=['+Name', '+Notes'])
    
    # Step 4: Verify the order of rows
    assert ordered_rows[0]["Name"] == "Alice" and ordered_rows[0]["Notes"] == "Note A", "First row ordering is incorrect."
    assert ordered_rows[1]["Name"] == "Alice" and ordered_rows[1]["Notes"] == "Note B", "Second row ordering is incorrect."
    assert ordered_rows[2]["Name"] == "Bob" and ordered_rows[2]["Notes"] == "Note A", "Third row ordering is incorrect."
    assert ordered_rows[3]["Name"] == "Bob" and ordered_rows[3]["Notes"] == "Note B", "Fourth row ordering is incorrect."

    # Step 5: Clean up by deleting the rows
    created_row_ids = [row.id for row in created_rows]
    if created_row_ids:
        all_fields_table.delete_rows(created_row_ids)


def test_get_rows_with_filter(all_fields_table, single_row_data):
    # Step 1: Generate data for multiple rows with varying "Name" values
    multiple_rows_data = generate_identical_rows(single_row_data, num_rows=4)
    
    # Customizing row data for filter test
    multiple_rows_data[0]["Name"]["input"] = "Grace"
    multiple_rows_data[1]["Name"]["input"] = "Grace"
    multiple_rows_data[2]["Name"]["input"] = "Alice"
    multiple_rows_data[3]["Name"]["input"] = "Bob"

    # Step 2: Create the rows
    input_data = [
        {key: value["input"] for key, value in row.items() if not value["read_only"]}
        for row in multiple_rows_data
    ]
    created_rows = all_fields_table.add_rows(input_data)
    
    # Step 3: Create a filter where the 'Name' field equals 'Grace'
    name_equal_grace = Filter("Name", "Grace")

    # Step 4: Fetch rows using the filter
    filtered_rows = all_fields_table.get_rows(filters=[name_equal_grace])
    
    # Step 5: Verify that only the correct rows are returned
    assert len(filtered_rows) == 2, f"Expected 2 rows, but got {len(filtered_rows)}"
    for row in filtered_rows:
        assert row["Name"] == "Grace", f"Expected row Name to be 'Grace', but got {row['Name']}"

    # Step 6: Clean up by deleting the rows
    created_row_ids = [row.id for row in created_rows]
    if created_row_ids:
        all_fields_table.delete_rows(created_row_ids)


def test_get_rows_with_number_filter(all_fields_table, single_row_data):
    # Step 1: Generate data for multiple rows with varying "Number" values
    multiple_rows_data = generate_identical_rows(single_row_data, num_rows=4)
    
    # Customizing row data for number filter test
    multiple_rows_data[0]["Number"]["input"] = 4
    multiple_rows_data[1]["Number"]["input"] = 6
    multiple_rows_data[2]["Number"]["input"] = 10
    multiple_rows_data[3]["Number"]["input"] = 3

    # Step 2: Create the rows
    input_data = [
        {key: value["input"] for key, value in row.items() if not value["read_only"]}
        for row in multiple_rows_data
    ]
    created_rows = all_fields_table.add_rows(input_data)
    
    # Step 3: Create a filter where the 'Number' field is higher than 5
    higher_than_5 = Filter('Number', 5, 'higher_than')

    # Step 4: Fetch rows using the filter
    filtered_rows = all_fields_table.get_rows(filters=[higher_than_5])
    
    # Step 5: Verify that only the correct rows are returned
    expected_numbers = {6.00, 10.00}  # Expecting floating-point numbers
    returned_numbers = {float(row["Number"]) for row in filtered_rows}

    assert returned_numbers == expected_numbers, f"Expected numbers {expected_numbers}, but got {returned_numbers}"

    # Step 6: Clean up by deleting the rows
    created_row_ids = [row.id for row in created_rows]
    if created_row_ids:
        all_fields_table.delete_rows(created_row_ids)


def test_get_rows_with_date_filter(all_fields_table, single_row_data):
    # Step 1: Generate data for multiple rows with varying "ISO Date" values
    multiple_rows_data = generate_identical_rows(single_row_data, num_rows=4)
    
    # Customizing row data for date filter test (using bare dates)
    multiple_rows_data[0]["ISO Date"]["input"] = "2010-01-01"  # Same date as filter, earlier
    multiple_rows_data[1]["ISO Date"]["input"] = "2010-01-02"  # Later date
    multiple_rows_data[2]["ISO Date"]["input"] = "2009-12-31"  # Different date, before filter date
    multiple_rows_data[3]["ISO Date"]["input"] = "2011-01-01"  # Later date

    # Step 2: Create the rows
    input_data = [
        {key: value["input"] for key, value in row.items() if not value["read_only"]}
        for row in multiple_rows_data
    ]
    created_rows = all_fields_table.add_rows(input_data)
    
    # Step 3: Create a filter where the 'ISO Date' field is after '2010-01-01'
    after_01_01_2010 = Filter('ISO Date', '2010-01-01', 'date_after')

    # Step 4: Fetch rows using the filter
    filtered_rows = all_fields_table.get_rows(filters=[after_01_01_2010])
    
    # Step 5: Verify that only the correct rows are returned
    expected_dates = {"2010-01-02", "2011-01-01"}  # Expecting these dates
    returned_dates = {row["ISO Date"] for row in filtered_rows}

    assert returned_dates == expected_dates, f"Expected dates {expected_dates}, but got {returned_dates}"

    # Step 6: Clean up by deleting the rows
    created_row_ids = [row.id for row in created_rows]
    if created_row_ids:
        all_fields_table.delete_rows(created_row_ids)

