from datetime import datetime

import pytest

pytestmark = pytest.mark.integration


def test_date_field_parse_value(all_fields_table, single_row_data):
    # Step 1: Create a single row with a specific ISO Date
    single_row_data["ISO Date"]["input"] = "2024-03-17"
    input_data = {
        key: value["input"] for key, value in single_row_data.items() if not value["read_only"]
    }
    created_row = all_fields_table.add_row(input_data)

    # Step 2: Parse explicitly through the field definition.
    parsed = all_fields_table.fields["ISO Date"].parse_value(
        created_row["ISO Date"]
    )

    # Step 3: Verify that the returned value is a datetime object
    assert parsed.isoformat() == "2024-03-17"

    # Step 4: Verify that the returned datetime object refers to the correct date
    expected_date = datetime(2024, 3, 17)
    assert parsed == expected_date.date()

    # Step 5: Clean up by deleting the row
    all_fields_table.delete_rows([created_row.id])


def test_date_field_format_value(all_fields_table, single_row_data):
    # Step 1: Create a single row with a specific US Date Time
    single_row_data["US Date Time"]["input"] = "2024-08-02T22:51:00Z"
    input_data = {
        key: value["input"] for key, value in single_row_data.items() if not value["read_only"]
    }
    created_row = all_fields_table.add_row(input_data)

    # Step 2: Format explicitly through the field definition.
    us_date_time_formatted = all_fields_table.fields["US Date Time"].format_value(
        created_row["US Date Time"]
    )

    # Step 3: Verify that the returned value is correctly formatted
    expected_format = '08-02-2024 10:51:00 PM UTC'
    assert us_date_time_formatted == expected_format, (
        f"Expected formatted date '{expected_format}', but got '{us_date_time_formatted}'"
    )

    # Step 4: Clean up by deleting the row
    all_fields_table.delete_rows([created_row.id])
