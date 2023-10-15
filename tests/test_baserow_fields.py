import pytest

from baserowapi import Baserow
from baserowapi.models.field import FieldList
from baserowapi.models.filter import Filter
from baserowapi.models.row import Row

import os

import datetime
import pytz


def test_text_field_properties_and_operations(table):
    # Get a single row with the specified filter and include parameters
    single_row = table.get_rows(
        include=["Name", "Last name"],
        filters=[Filter("Last name", "Kitty")],
        return_single=True,
    )

    # Ensure that a row was returned and it's of the correct type
    assert single_row is not None, "No row was returned but one was expected."
    assert isinstance(
        single_row, Row
    ), f"Expected a Row object, but got {type(single_row)}."

    # Check that the table has a field "Name" of type "text"
    assert "Name" in table.fields, "Field 'Name' not found in table fields."
    assert (
        table.fields["Name"].type == "text"
    ), f"Expected field 'Name' to be of type 'text', but got {table.fields['Name'].type}."

    # Check that the default text property of the field is correctly set
    assert (
        table.fields["Name"].text_default == "default text for Name field"
    ), f"Expected default text for 'Name' field to be 'default text for Name field', but got {table.fields['Name'].text_default}."

    # Check that the row has a value "Name" of type "text"
    assert (
        single_row.values["Name"].type == "text"
    ), f"Expected RowValue 'Name' to be of type 'text', but got {single_row.values['Name'].type}."

    # Change the value in memory
    single_row["Name"] = "Ema"

    # Update the row with the new value
    updated_row = single_row.update()

    # Check that the updated row has the expected new value
    assert (
        updated_row["Name"] == "Ema"
    ), f"Expected 'Ema' for 'Name' after update, but got {updated_row['Name']}."


def test_long_text_field_properties_and_operations(table):
    # Get a single row with the specified filter and include parameters
    single_row = table.get_rows(
        include=["Last name", "Notes"],
        filters=[Filter("Last name", "Kitty")],
        return_single=True,
    )

    # Ensure that a row was returned and it's of the correct type
    assert single_row is not None, "No row was returned but one was expected."
    assert isinstance(
        single_row, Row
    ), f"Expected a Row object, but got {type(single_row)}."

    # Check that the table has a field "Notes" of type "long_text"
    assert "Notes" in table.fields, "Field 'Notes' not found in table fields."
    assert (
        table.fields["Notes"].type == "long_text"
    ), f"Expected field 'Notes' to be of type 'long_text', but got {table.fields['Notes'].type}."

    # Check that the row has a value "Notes" of type "long_text"
    assert (
        single_row.values["Notes"].type == "long_text"
    ), f"Expected RowValue 'Notes' to be of type 'long_text', but got {single_row.values['Notes'].type}."

    # Change the value in memory
    single_row["Notes"] = "Extended note for Ema."

    # Update the row with the new value
    updated_row = single_row.update()

    # Check that the updated row has the expected new value
    assert (
        updated_row["Notes"] == "Extended note for Ema."
    ), f"Expected 'Extended note for Ema.' for 'Notes' after update, but got {updated_row['Notes']}."


def test_url_field_properties_and_operations(table):
    # Get a single row with the specified filter and include parameters
    single_row = table.get_rows(
        include=["Name", "Last name", "myURL"],
        filters=[Filter("Last name", "Kitty")],
        return_single=True,
    )

    # Ensure that a row was returned and it's of the correct type
    assert single_row is not None, "No row was returned but one was expected."
    assert isinstance(
        single_row, Row
    ), f"Expected a Row object, but got {type(single_row)}."

    # Check that the table has a field "myURL" of type "url"
    assert "myURL" in table.fields, "Field 'myURL' not found in table fields."
    assert (
        table.fields["myURL"].type == "url"
    ), f"Expected field 'myURL' to be of type 'url', but got {table.fields['myURL'].type}."

    # Check that the row has a value "myURL" of type "url"
    assert (
        single_row.values["myURL"].type == "url"
    ), f"Expected RowValue 'myURL' to be of type 'url', but got {single_row.values['myURL'].type}."

    # Change the value in memory
    single_row["myURL"] = "https://example.com"

    # Update the row with the new value
    updated_row = single_row.update()

    # Check that the updated row has the expected new value
    assert (
        updated_row["myURL"] == "https://example.com"
    ), f"Expected 'https://example.com' for 'myURL' after update, but got {updated_row['myURL']}."


def test_email_field_properties_and_operations(table):
    # Get a single row with the specified filter and include parameters
    single_row = table.get_rows(
        include=["Name", "Last name", "myEmail"],
        filters=[Filter("Last name", "Kitty")],
        return_single=True,
    )

    # Ensure that a row was returned and it's of the correct type
    assert single_row is not None, "No row was returned but one was expected."
    assert isinstance(
        single_row, Row
    ), f"Expected a Row object, but got {type(single_row)}."

    # Check that the table has a field "myEmail" of type "email"
    assert "myEmail" in table.fields, "Field 'myEmail' not found in table fields."
    assert (
        table.fields["myEmail"].type == "email"
    ), f"Expected field 'myEmail' to be of type 'email', but got {table.fields['myEmail'].type}."

    # Check that the row has a value "myEmail" of type "email"
    assert (
        single_row.values["myEmail"].type == "email"
    ), f"Expected RowValue 'myEmail' to be of type 'email', but got {single_row.values['myEmail'].type}."

    # Change the value in memory
    single_row["myEmail"] = "example@example.com"

    # Update the row with the new value
    updated_row = single_row.update()

    # Check that the updated row has the expected new value
    assert (
        updated_row["myEmail"] == "example@example.com"
    ), f"Expected 'example@example.com' for 'myEmail' after update, but got {updated_row['myEmail']}."


def test_phone_number_field_properties_and_operations(table):
    # Get a single row with the specified filter and include parameters
    single_row = table.get_rows(
        include=["Name", "Last name", "myPhone"],
        filters=[Filter("Last name", "Kitty")],
        return_single=True,
    )

    # Ensure that a row was returned and it's of the correct type
    assert single_row is not None, "No row was returned but one was expected."
    assert isinstance(
        single_row, Row
    ), f"Expected a Row object, but got {type(single_row)}."

    # Check that the table has a field "myPhone" of type "phone_number"
    assert "myPhone" in table.fields, "Field 'myPhone' not found in table fields."
    assert (
        table.fields["myPhone"].type == "phone_number"
    ), f"Expected field 'myPhone' to be of type 'phone_number', but got {table.fields['myPhone'].type}."

    # Check that the row has a value "myPhone" of type "phone_number"
    assert (
        single_row.values["myPhone"].type == "phone_number"
    ), f"Expected RowValue 'myPhone' to be of type 'phone_number', but got {single_row.values['myPhone'].type}."

    # Change the value in memory
    single_row["myPhone"] = "555-555-5555"

    # Update the row with the new value
    updated_row = single_row.update()

    # Check that the updated row has the expected new value
    assert (
        updated_row["myPhone"] == "555-555-5555"
    ), f"Expected '555-555-5555' for 'myPhone' after update, but got {updated_row['myPhone']}."


def test_boolean_field_properties_and_operations(table):
    # Get a single row with the specified filter and include parameters
    single_row = table.get_rows(
        include=["Name", "Last name", "Active"],
        filters=[Filter("Last name", "Kitty")],
        return_single=True,
    )

    # Ensure that a row was returned and it's of the correct type
    assert single_row is not None, "No row was returned but one was expected."
    assert isinstance(
        single_row, Row
    ), f"Expected a Row object, but got {type(single_row)}."

    # Check that the table has a field "Active" of type "boolean"
    assert "Active" in table.fields, "Field 'Active' not found in table fields."
    assert (
        table.fields["Active"].type == "boolean"
    ), f"Expected field 'Active' to be of type 'boolean', but got {table.fields['Active'].type}."

    # Check that the row has a value "Active" of type "boolean"
    assert (
        single_row.values["Active"].type == "boolean"
    ), f"Expected RowValue 'Active' to be of type 'boolean', but got {single_row.values['Active'].type}."

    # Change the value in memory
    single_row["Active"] = False

    # Update the row with the new value
    updated_row = single_row.update()

    # Check that the updated row has the expected new value
    assert (
        updated_row["Active"] is False
    ), f"Expected False for 'Active' after update, but got {updated_row['Active']}."


def test_number_field_properties_and_operations(table):
    # Get a single row with the specified filter and include parameters
    single_row = table.get_rows(
        include=["Name", "Last name", "myNumber"],
        filters=[Filter("Last name", "Kitty")],
        return_single=True,
    )

    # Ensure that a row was returned and it's of the correct type
    assert single_row is not None, "No row was returned but one was expected."
    assert isinstance(
        single_row, Row
    ), f"Expected a Row object, but got {type(single_row)}."

    # Check that the table has a field "myNumber" of type "number"
    assert "myNumber" in table.fields, "Field 'myNumber' not found in table fields."
    assert (
        table.fields["myNumber"].type == "number"
    ), f"Expected field 'myNumber' to be of type 'number', but got {table.fields['myNumber'].type}."

    # Check that the row has a value "myNumber" of type "number"
    assert (
        single_row.values["myNumber"].type == "number"
    ), f"Expected RowValue 'myNumber' to be of type 'number', but got {single_row.values['myNumber'].type}."

    # Check properties for the number type
    assert isinstance(
        table.fields["myNumber"].number_decimal_places, int
    ), f"Expected 'number_decimal_places' property to be integer for 'myNumber', but got {type(table.fields['myNumber'].number_decimal_places)}."
    assert isinstance(
        table.fields["myNumber"].number_negative, bool
    ), f"Expected 'number_negative' property to be boolean for 'myNumber', but got {type(table.fields['myNumber'].number_negative)}."

    # Change the value in memory
    single_row["myNumber"] = 42.5

    # Update the row with the new value
    updated_row = single_row.update()

    # Check that the updated row has the expected new value
    expected_value = float(f"{42.5:.{table.fields['myNumber'].number_decimal_places}f}")

    # Convert the value from updated_row to float and then compare
    assert (
        float(updated_row["myNumber"]) == expected_value
    ), f"Expected {expected_value} for 'myNumber' after update, but got {updated_row['myNumber']}."


def test_rating_field_properties_and_operations(table):
    # Get a single row with the specified filter and include parameters
    single_row = table.get_rows(
        include=["Name", "Last name", "myRating"],
        filters=[Filter("Last name", "Kitty")],
        return_single=True,
    )

    # Ensure that a row was returned and it's of the correct type
    assert single_row is not None, "No row was returned but one was expected."
    assert isinstance(
        single_row, Row
    ), f"Expected a Row object, but got {type(single_row)}."

    # Check that the table has a field "myRating" of type "rating"
    assert "myRating" in table.fields, "Field 'myRating' not found in table fields."
    assert (
        table.fields["myRating"].type == "rating"
    ), f"Expected field 'myRating' to be of type 'rating', but got {table.fields['myRating'].type}."

    # Check that the row has a value "myRating" of type "rating"
    assert (
        single_row.values["myRating"].type == "rating"
    ), f"Expected RowValue 'myRating' to be of type 'rating', but got {single_row.values['myRating'].type}."

    # Check properties for the rating type
    assert isinstance(
        table.fields["myRating"].max_value, int
    ), f"Expected 'max_value' property to be integer for 'myRating', but got {type(table.fields['myRating'].max_value)}."
    assert isinstance(
        table.fields["myRating"].color, str
    ), f"Expected 'color' property to be string for 'myRating', but got {type(table.fields['myRating'].color)}."
    assert isinstance(
        table.fields["myRating"].style, str
    ), f"Expected 'style' property to be string for 'myRating', but got {type(table.fields['myRating'].style)}."

    # Change the value in memory. The value will be set to 3, assuming max_value is 5. Adjust accordingly if needed.
    single_row["myRating"] = 3

    # Update the row with the new value
    updated_row = single_row.update()

    # Check that the updated row has the expected new value
    assert (
        updated_row["myRating"] == 3
    ), f"Expected 3 for 'myRating' after update, but got {updated_row['myRating']}."


def test_date_field_properties_and_operations(table):
    # Get a single row with the specified filter and include parameters
    single_row = table.get_rows(
        include=["Name", "Last name", "US Date Time"],
        filters=[Filter("Last name", "Kitty")],
        return_single=True,
    )

    # Ensure that a row was returned and it's of the correct type
    assert single_row is not None, "No row was returned but one was expected."
    assert isinstance(
        single_row, Row
    ), f"Expected a Row object, but got {type(single_row)}."

    # Check that the table has a field "US Date Time" of type "date"
    assert (
        "US Date Time" in table.fields
    ), "Field 'US Date Time' not found in table fields."
    assert (
        table.fields["US Date Time"].type == "date"
    ), f"Expected field 'US Date Time' to be of type 'date', but got {table.fields['US Date Time'].type}."

    # Check properties for the date type
    date_field = table.fields["US Date Time"]
    assert isinstance(date_field.date_format, str)
    assert isinstance(date_field.date_include_time, bool)
    assert isinstance(date_field.date_time_format, str)
    assert isinstance(date_field.date_show_tzinfo, bool)

    # Change the value in memory using string in ISO UTC date format
    print(f"ISO date: {single_row['US Date Time']}")
    test_date_str = "2022-05-01T14:30:00Z"
    single_row["US Date Time"] = test_date_str
    updated_row = single_row.update()
    assert (
        updated_row["US Date Time"] == test_date_str
    ), f"Expected {test_date_str} for 'US Date Time' after update using string, but got {updated_row['US Date Time']}."

    # Change the value in memory using a python datetime object
    test_date_obj = datetime.datetime(
        2022, 5, 1, 15, 30, tzinfo=pytz.UTC
    )  # Make the datetime object timezone-aware

    # Convert the datetime object to the required format for Baserow
    formatted_date_obj = test_date_obj.isoformat().replace("+00:00", "Z")

    single_row["US Date Time"] = formatted_date_obj
    updated_row = single_row.update()

    # Check that the updated row has the expected new value
    assert (
        updated_row["US Date Time"] == formatted_date_obj
    ), f"Expected {formatted_date_obj} for 'US Date Time' after update using datetime object, but got {updated_row['US Date Time']}."

    # Test the rowValue object's as_datetime and formatted_date methods
    date_row_value = single_row.values["US Date Time"]
    assert (
        date_row_value.as_datetime() == test_date_obj
    ), f"Expected datetime object {test_date_obj} from as_datetime(), but got {date_row_value.as_datetime()}."

    # format the date according to the field's properties.
    expected_formatted_date = "05-01-2022 10:30:00 CDT"
    assert (
        date_row_value.formatted_date == expected_formatted_date
    ), f"Expected formatted date {expected_formatted_date}, but got {date_row_value.formatted_date}."


def test_last_modified_field_properties_and_operations(table):
    # Get a single row with the specified filter and include parameters
    single_row = table.get_rows(
        include=["Name", "Last name", "Last modified"],
        filters=[Filter("Last name", "Kitty")],
        return_single=True,
    )

    # Ensure that a row was returned and it's of the correct type
    assert single_row is not None, "No row was returned but one was expected."
    assert isinstance(
        single_row, Row
    ), f"Expected a Row object, but got {type(single_row)}."

    # Check that the table has a field "Last modified" of type "last_modified"
    assert (
        "Last modified" in table.fields
    ), "Field 'Last modified' not found in table fields."
    assert (
        table.fields["Last modified"].type == "last_modified"
    ), f"Expected field 'Last modified' to be of type 'last_modified', but got {table.fields['Last modified'].type}."

    # Check that the field has a property "is_read_only" set to true
    assert table.fields[
        "Last modified"
    ].is_read_only, (
        "Expected 'is_read_only' property of field 'Last modified' to be True."
    )

    # Attempt to change the value and confirm that it raises an exception
    try:
        single_row["Last modified"] = "2023-10-01T14:30:00Z"
        single_row.update()
    except Exception as e:
        assert isinstance(
            e, ValueError
        ), "Setting a value for 'Last modified' should have raised an exception, but a different exception was encountered."

    # Check that the value is of type string
    assert isinstance(
        single_row["Last modified"], str
    ), f"Expected a string value for 'Last modified', but got {type(single_row['Last modified'])}."


def test_created_on_field_properties_and_operations(table):
    # Get a single row with the specified filter and include parameters
    single_row = table.get_rows(
        include=["Name", "Last name", "Created on"],
        filters=[Filter("Last name", "Kitty")],
        return_single=True,
    )

    # Ensure that a row was returned and it's of the correct type
    assert single_row is not None, "No row was returned but one was expected."
    assert isinstance(
        single_row, Row
    ), f"Expected a Row object, but got {type(single_row)}."

    # Check that the table has a field "Created on" of type "created_on"
    assert "Created on" in table.fields, "Field 'Created on' not found in table fields."
    assert (
        table.fields["Created on"].type == "created_on"
    ), f"Expected field 'Created on' to be of type 'created_on', but got {table.fields['Created on'].type}."

    # Check that the field has a property "is_read_only" set to true
    assert table.fields[
        "Created on"
    ].is_read_only, "Expected 'is_read_only' property of field 'Created on' to be True."

    # Attempt to change the value and confirm that it raises an exception
    try:
        single_row["Created on"] = "2023-10-01T14:30:00Z"
        single_row.update()
    except ValueError:
        pass  # This exception is expected since the field is read-only
    else:
        assert (
            False
        ), "Setting a value for 'Created on' should have raised a ValueError."

    # Ensure that the value is a string (date in string format)
    assert isinstance(
        single_row["Created on"], str
    ), f"Expected 'Created on' value to be a string, but got {type(single_row['Created on'])}."


def test_single_select_field_properties_and_operations(table):
    # Get a single row with the specified filter and include parameters
    single_row = table.get_rows(
        include=["Name", "Last name", "mySingleSelect"],
        filters=[Filter("Last name", "Kitty")],
        return_single=True,
    )

    # Ensure that a row was returned and it's of the correct type
    assert single_row is not None, "No row was returned but one was expected."
    assert isinstance(
        single_row, Row
    ), f"Expected a Row object, but got {type(single_row)}."

    # Check that the table has a field "mySingleSelect" of type "single_select"
    assert (
        "mySingleSelect" in table.fields
    ), "Field 'mySingleSelect' not found in table fields."
    assert (
        table.fields["mySingleSelect"].type == "single_select"
    ), f"Expected field 'mySingleSelect' to be of type 'single_select', but got {table.fields['mySingleSelect'].type}."

    # Check that the field has the properties 'options' and 'options_details'
    single_select_field = table.fields["mySingleSelect"]
    assert hasattr(
        single_select_field, "options"
    ), "Field 'mySingleSelect' doesn't have the 'options' property."
    assert hasattr(
        single_select_field, "options_details"
    ), "Field 'mySingleSelect' doesn't have the 'options_details' property."

    # Check if both properties return lists
    assert isinstance(
        single_select_field.options, list
    ), f"Expected 'options' property of 'mySingleSelect' field to be a list, but got {type(single_select_field.options)}."
    assert isinstance(
        single_select_field.options_details, list
    ), f"Expected 'options_details' property of 'mySingleSelect' field to be a list, but got {type(single_select_field.options_details)}."

    # Try setting a valid value from the options
    if single_select_field.options:  # If there are any options available
        valid_value = single_select_field.options[0]
        single_row["mySingleSelect"] = valid_value
        updated_row = single_row.update()
        assert (
            updated_row["mySingleSelect"] == valid_value
        ), f"Expected {valid_value} for 'mySingleSelect' after update, but got {updated_row['mySingleSelect']}."

    # Try setting an invalid value and ensure it raises an error
    invalid_value = "InvalidOptionThatShouldNotBeInTheList"
    try:
        single_row["mySingleSelect"] = invalid_value
        single_row.update()
    except ValueError:
        pass  # This exception is expected since we're trying to set an invalid option
    else:
        assert (
            False
        ), f"Setting an invalid value '{invalid_value}' for 'mySingleSelect' should have raised a ValueError."


def test_multiple_select_field_properties_and_operations(table):
    # Get a single row with the specified filter and include parameters
    single_row = table.get_rows(
        include=["Name", "Last name", "myMultipleSelect"],
        filters=[Filter("Last name", "Kitty")],
        return_single=True,
    )

    # Ensure that a row was returned and it's of the correct type
    assert single_row is not None, "No row was returned but one was expected."
    assert isinstance(
        single_row, Row
    ), f"Expected a Row object, but got {type(single_row)}."

    # Check that the table has a field "myMultipleSelect" of type "multiple_select"
    assert (
        "myMultipleSelect" in table.fields
    ), "Field 'myMultipleSelect' not found in table fields."
    assert (
        table.fields["myMultipleSelect"].type == "multiple_select"
    ), f"Expected field 'myMultipleSelect' to be of type 'multiple_select', but got {table.fields['myMultipleSelect'].type}."

    # Check that the field has the properties 'options' and 'options_details'
    multiple_select_field = table.fields["myMultipleSelect"]
    assert hasattr(
        multiple_select_field, "options"
    ), "Field 'myMultipleSelect' doesn't have the 'options' property."
    assert hasattr(
        multiple_select_field, "options_details"
    ), "Field 'myMultipleSelect' doesn't have the 'options_details' property."

    # Check if both properties return lists
    assert isinstance(
        multiple_select_field.options, list
    ), f"Expected 'options' property of 'myMultipleSelect' field to be a list, but got {type(multiple_select_field.options)}."
    assert isinstance(
        multiple_select_field.options_details, list
    ), f"Expected 'options_details' property of 'myMultipleSelect' field to be a list, but got {type(multiple_select_field.options_details)}."

    # Try setting multiple valid values from the options
    if multiple_select_field.options:  # If there are any options available
        valid_values = multiple_select_field.options[
            :2
        ]  # Take the first two options as an example
        single_row["myMultipleSelect"] = valid_values
        updated_row = single_row.update()
        assert set(updated_row["myMultipleSelect"]) == set(
            valid_values
        ), f"Expected {valid_values} for 'myMultipleSelect' after update, but got {updated_row['myMultipleSelect']}."

    # Try setting some invalid values and ensure it raises an error
    invalid_values = ["InvalidOption1", "InvalidOption2"]
    try:
        single_row["myMultipleSelect"] = invalid_values
        single_row.update()
    except ValueError:
        pass  # This exception is expected since we're trying to set invalid options
    else:
        assert (
            False
        ), f"Setting invalid values '{invalid_values}' for 'myMultipleSelect' should have raised a ValueError."

    # Setting the field to empty list to represent no selection
    single_row["myMultipleSelect"] = []
    updated_row = single_row.update()
    assert (
        updated_row["myMultipleSelect"] == []
    ), f"Expected 'myMultipleSelect' to be None after update, but got {updated_row['myMultipleSelect']}."


def test_formula_field_properties_and_operations(table):
    # Get a single row with the specified filter and include parameters
    single_row = table.get_rows(
        include=["Name", "Last name", "myFormula"],
        filters=[Filter("Last name", "Kitty")],
        return_single=True,
    )

    # Ensure that a row was returned and it's of the correct type
    assert single_row is not None, "No row was returned but one was expected."
    assert isinstance(
        single_row, Row
    ), f"Expected a Row object, but got {type(single_row)}."

    # Check that the table has a field "myFormula" of type "formula"
    assert "myFormula" in table.fields, "Field 'myFormula' not found in table fields."
    assert (
        table.fields["myFormula"].type == "formula"
    ), f"Expected field 'myFormula' to be of type 'formula', but got {table.fields['myFormula'].type}."

    # Retrieve the formula field
    formula_field = table.fields["myFormula"]

    # Check the properties of the formula field
    assert hasattr(
        formula_field, "formula"
    ), "Field 'myFormula' doesn't have the 'formula' property."
    assert hasattr(
        formula_field, "formula_type"
    ), "Field 'myFormula' doesn't have the 'formula_type' property."
    assert hasattr(
        formula_field, "error"
    ), "Field 'myFormula' doesn't have the 'error' property."
    assert hasattr(
        formula_field, "array_formula_type"
    ), "Field 'myFormula' doesn't have the 'array_formula_type' property."
    assert hasattr(
        formula_field, "is_read_only"
    ), "Field 'myFormula' doesn't have the 'is_read_only' property."

    # Check that the field has a property "is_read_only" set to true
    assert (
        formula_field.is_read_only
    ), "Expected 'is_read_only' property of field 'myFormula' to be True."

    # Attempt to change the value and confirm that it raises an exception
    try:
        single_row["myFormula"] = "INVALID_FORMULA_VALUE"
        single_row.update()
    except ValueError:
        pass  # This exception is expected since we're trying to set a read-only field
    else:
        assert False, "Setting a value for 'myFormula' should have raised a ValueError."


def test_link_row_field_properties_and_operations(table):
    # Get a single row with the specified filter and include parameters
    single_row = table.get_rows(
        include=["Name", "Last name", "myTableLink"],
        filters=[Filter("Last name", "Kitty")],
        return_single=True,
    )

    # Ensure that a row was returned and it's of the correct type
    assert single_row is not None, "No row was returned but one was expected."
    assert isinstance(
        single_row, Row
    ), f"Expected a Row object, but got {type(single_row)}."

    # Check that the table has a field "myTableLink" of type "link_row"
    assert (
        "myTableLink" in table.fields
    ), "Field 'myTableLink' not found in table fields."
    assert (
        table.fields["myTableLink"].type == "link_row"
    ), f"Expected field 'myTableLink' to be of type 'link_row', but got {table.fields['myTableLink'].type}."

    # Retrieve the link_row field
    link_row_field = table.fields["myTableLink"]

    # Check the properties of the link_row field
    properties = [
        "link_row_table_id",
        "link_row_related_field_id",
        "link_row_table",
        "link_row_related_field",
    ]
    for prop in properties:
        assert hasattr(
            link_row_field, prop
        ), f"Field 'myTableLink' doesn't have the '{prop}' property."

    # Testing the RowValue methods
    # Test get_options()
    options = single_row.values["myTableLink"].get_options()
    assert isinstance(options, list), "Expected get_options() method to return a list."

    # Test get_related_table()
    related_table = single_row.values["myTableLink"].get_related_table()
    assert (
        related_table
    ), "Expected get_related_table() method to return a table object."

    # Updating value using primary row values
    if options:
        single_row["myTableLink"] = options[:2]  # Using first two options as an example
        updated_row = single_row.update()
        assert set(updated_row["myTableLink"]) == set(
            options[:2]
        ), f"Expected {options[:2]} for 'myTableLink' after update, but got {updated_row['myTableLink']}."

    # Updating value using row ids.
    valid_ids = [1, 2]
    expected_values = ["Fred", "Neil"]
    single_row["myTableLink"] = valid_ids
    updated_row = single_row.update()
    assert set(updated_row["myTableLink"]) == set(
        expected_values
    ), f"Expected {expected_values} for 'myTableLink' after update using ids, but got {updated_row['myTableLink']}."


def test_count_field_properties_and_operations(table):
    # Get a single row with the specified filter and include parameters
    single_row = table.get_rows(
        include=["Name", "Last name", "myCount"],
        filters=[Filter("Last name", "Kitty")],
        return_single=True,
    )

    # Ensure that a row was returned and it's of the correct type
    assert single_row is not None, "No row was returned but one was expected."
    assert isinstance(
        single_row, Row
    ), f"Expected a Row object, but got {type(single_row)}."

    # Check that the table has a field "myCount" of type "count"
    assert "myCount" in table.fields, "Field 'myCount' not found in table fields."
    assert (
        table.fields["myCount"].type == "count"
    ), f"Expected field 'myCount' to be of type 'count', but got {table.fields['myCount'].type}."

    # Retrieve the count field
    count_field = table.fields["myCount"]

    # Check the properties of the count field
    properties = ["through_field_id", "is_read_only"]
    for prop in properties:
        assert hasattr(
            count_field, prop
        ), f"Field 'myCount' doesn't have the '{prop}' property."

    assert (
        count_field.is_read_only
    ), "Expected 'is_read_only' property of field 'myCount' to be True."

    # Try to update the value and expect it to raise an error
    try:
        single_row["myCount"] = 5
        single_row.update()
    except Exception as e:
        assert isinstance(
            e, ValueError
        ), "Setting a value for 'myCount' should have raised a ValueError, but a different exception was encountered."
    else:
        assert (
            False
        ), "Updating the 'myCount' field should have raised an exception, but it did not."


def test_lookup_field_properties_and_operations(table):
    # Get a single row with the specified filter and include parameters
    single_row = table.get_rows(
        include=["Name", "Last name", "myLookup"],
        filters=[Filter("Last name", "Kitty")],
        return_single=True,
    )

    # Ensure that a row was returned and it's of the correct type
    assert single_row is not None, "No row was returned but one was expected."
    assert isinstance(
        single_row, Row
    ), f"Expected a Row object, but got {type(single_row)}."

    # Check that the table has a field "myLookup" of type "lookup"
    assert "myLookup" in table.fields, "Field 'myLookup' not found in table fields."
    assert (
        table.fields["myLookup"].type == "lookup"
    ), f"Expected field 'myLookup' to be of type 'lookup', but got {table.fields['myLookup'].type}."

    # Retrieve the lookup field
    lookup_field = table.fields["myLookup"]

    # Check the properties of the lookup field
    properties = [
        "through_field_id",
        "through_field_name",
        "target_field_id",
        "target_field_name",
        "is_read_only",
    ]
    for prop in properties:
        assert hasattr(
            lookup_field, prop
        ), f"Field 'myLookup' doesn't have the '{prop}' property."

    assert (
        lookup_field.is_read_only
    ), "Expected 'is_read_only' property of field 'myLookup' to be True."

    # Try to update the value and expect it to raise an error
    try:
        single_row["myLookup"] = "SomeValue"
        single_row.update()
    except Exception as e:
        assert isinstance(
            e, ValueError
        ), "Setting a value for 'myLookup' should have raised a ValueError, but a different exception was encountered."
    else:
        assert (
            False
        ), "Updating the 'myLookup' field should have raised an exception, but it did not."


def test_multiple_collaborators_field_properties_and_operations(table):
    # Get a single row with the specified filter and include parameters
    single_row = table.get_rows(
        include=["Name", "Last name", "myCollaborators"],
        filters=[Filter("Last name", "Kitty")],
        return_single=True,
    )

    # Ensure that a row was returned and it's of the correct type
    assert single_row is not None, "No row was returned but one was expected."
    assert isinstance(
        single_row, Row
    ), f"Expected a Row object, but got {type(single_row)}."

    # Check that the table has a field "myCollaborators" of type "multiple_collaborators"
    assert (
        "myCollaborators" in table.fields
    ), "Field 'myCollaborators' not found in table fields."
    assert (
        table.fields["myCollaborators"].type == "multiple_collaborators"
    ), f"Expected field 'myCollaborators' to be of type 'multiple_collaborators', but got {table.fields['myCollaborators'].type}."

    # Retrieve the multiple_collaborators field
    multiple_collaborators_field = table.fields["myCollaborators"]

    # Check the properties of the multiple_collaborators field
    properties = ["notify_user_when_added"]
    for prop in properties:
        assert hasattr(
            multiple_collaborators_field, prop
        ), f"Field 'myCollaborators' doesn't have the '{prop}' property."

    # Check if "notify_user_when_added" property is a boolean
    assert isinstance(
        multiple_collaborators_field.notify_user_when_added, bool
    ), "Expected 'notify_user_when_added' property to be a boolean."

    # Update the field value to an empty list (removing all collaborators)
    single_row["myCollaborators"] = []
    updated_row = single_row.update()
    assert not updated_row[
        "myCollaborators"
    ], "Expected 'myCollaborators' field to be empty after update, but it was not."


@pytest.mark.wip
def test_file_field_properties_and_operations(table):
    # Get a single row with the specified filter and include parameters
    single_row = table.get_rows(
        include=["Name", "Last name", "myFileField"],
        filters=[Filter("Last name", "Kitty")],
        return_single=True,
    )

    # Ensure that a row was returned and it's of the correct type
    assert single_row is not None, "No row was returned but one was expected."
    assert isinstance(
        single_row, Row
    ), f"Expected a Row object, but got {type(single_row)}."

    # Check that the table has a field "myFileField" of type "file"
    assert (
        "myFileField" in table.fields
    ), "Field 'myFileField' not found in table fields."
    assert (
        table.fields["myFileField"].type == "file"
    ), f"Expected field 'myFileField' to be of type 'file', but got {table.fields['myFileField'].type}."

    # Upload a local file
    files_uploaded = single_row.values["myFileField"].upload_file_to_server(
        file_path="fixie.jpg"
    )
    assert "fixie.jpg" in [
        file_obj["original_name"] for file_obj in files_uploaded
    ], "Local file 'fixie.jpg' was not uploaded correctly."

    # Upload a file from a URL
    files_uploaded_from_url = single_row.values["myFileField"].upload_file_to_server(
        url="https://www.jimwitte.net/bison.jpg"
    )
    assert "bison.jpg" in [
        file_obj["original_name"] for file_obj in files_uploaded_from_url
    ], "File 'bison.jpg' was not uploaded from URL correctly."

    # Download the files to a directory
    directory_path = "/tmp"
    downloaded_files = single_row.values["myFileField"].download_files(
        directory_path=directory_path
    )
    expected_files = ["fixie.jpg", "bison.jpg"]
    for expected_file in expected_files:
        assert (
            expected_file in downloaded_files
        ), f"Expected {expected_file} to be downloaded, but it was not."
        # Also ensure the file exists in the directory
        assert os.path.exists(
            os.path.join(directory_path, expected_file)
        ), f"{expected_file} was not found in the download directory."

    # Clear files from the RowValue object and update the row
    single_row["myFileField"] = []
    updated_row = single_row.update()
    assert not updated_row[
        "myFileField"
    ], "Files should have been removed from 'myFileField', but they were not."

    # Cleanup: Delete the downloaded files from the directory for future test runs
    for expected_file in expected_files:
        os.remove(os.path.join(directory_path, expected_file))
