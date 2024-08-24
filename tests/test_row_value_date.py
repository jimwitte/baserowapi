import pytest
from datetime import datetime

def test_rowvalue_as_datetime(all_fields_table, single_row_data):
    # Step 1: Create a single row with a specific ISO Date
    single_row_data["ISO Date"]["input"] = "2024-03-17"
    input_data = {
        key: value["input"] for key, value in single_row_data.items() if not value["read_only"]
    }
    created_row = all_fields_table.add_rows([input_data])[0]

    # Step 2: Access the as_datetime() function
    iso_date_as_datetime = created_row.values["ISO Date"].as_datetime()

    # Step 3: Verify that the returned value is a datetime object
    assert isinstance(iso_date_as_datetime, datetime), (
        f"Expected a datetime object, but got {type(iso_date_as_datetime)}"
    )

    # Step 4: Verify that the returned datetime object refers to the correct date
    expected_date = datetime(2024, 3, 17)
    assert iso_date_as_datetime.date() == expected_date.date(), (
        f"Expected date {expected_date.date()}, but got {iso_date_as_datetime.date()}"
    )

    # Step 5: Clean up by deleting the row
    all_fields_table.delete_rows([created_row.id])


def test_rowvalue_formatted_date(all_fields_table, single_row_data):
    # Step 1: Create a single row with a specific US Date Time
    single_row_data["US Date Time"]["input"] = "2024-08-02T22:51:00Z"
    input_data = {
        key: value["input"] for key, value in single_row_data.items() if not value["read_only"]
    }
    created_row = all_fields_table.add_rows([input_data])[0]

    # Step 2: Access the formatted_date property
    us_date_time_formatted = created_row.values["US Date Time"].formatted_date

    # Step 3: Verify that the returned value is correctly formatted
    expected_format = '08-02-2024 10:51:00 PM UTC'
    assert us_date_time_formatted == expected_format, (
        f"Expected formatted date '{expected_format}', but got '{us_date_time_formatted}'"
    )

    # Step 4: Clean up by deleting the row
    all_fields_table.delete_rows([created_row.id])
