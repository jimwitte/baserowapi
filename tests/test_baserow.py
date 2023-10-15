import pytest

from baserowapi import Baserow
from baserowapi.models.field import FieldList
from baserowapi.models.filter import Filter
from baserowapi.models.row import Row


def test_baserow_instantiation(baserow_client):
    """Test if the Baserow instance is correctly instantiated."""

    assert isinstance(baserow_client, Baserow), "Baserow client instantiation failed"


def test_table_instantiation(table):
    """Test that a table can be instantiated using the table fixture."""
    assert table is not None  # Ensure the table object is instantiated
    assert table.id == 198958  # Ensure the table ID matches the expected ID


def test_table_primary_field_set(table):
    """Test that the table's primary field is set."""
    assert table.primary_field is not None


def test_table_fields_type(table):
    """Test that the table's fields are of type FieldList."""
    assert isinstance(table.fields, FieldList)


def test_table_field_names_set(table):
    """Test that the table's field names are set."""
    assert table.field_names is not None
    assert isinstance(table.field_names, list)  # Ensure field_names is a list
    assert len(table.field_names) > 0  # Ensure the list is not empty


def test_table_field_name_type(table):
    """Test the type of the field with key 'Name'."""
    field = next((f for f in table.fields if f.name == "Name"), None)
    assert field is not None  # Ensure the field exists
    assert field.type == "text"


def test_table_get_row_by_id(table):
    """Test fetching a row by its ID."""
    row = table.get_row(1)
    assert row is not None
    assert row.id == 1


def test_row_values_set(table):
    """Test that values of a row are set."""
    row = table.get_row(1)
    assert row.values is not None


def test_row_content_non_empty(table):
    """Test that the content of a row is a non-empty dictionary."""
    row = table.get_row(1)
    assert isinstance(row.content, dict)
    assert len(row.content) > 0


def test_row_name_value(table):
    """Test the value of the 'Name' field in a row."""
    row = table.get_row(1)
    assert row.content["Name"] == "Spot"


def test_get_all_rows_returns_row_iterator(table):
    """Test fetching all rows returns a RowIterator object."""
    rows = table.get_rows()
    assert isinstance(rows, table.RowIterator)


def test_get_all_rows_count(table):
    """Test the number of rows returned by the get_rows method."""
    rows = table.get_rows()
    assert len(list(rows)) == 7


def test_filter_query_string():
    name_equal_grace = Filter("Name", "Grace")
    assert name_equal_grace.query_string == "filter__Name__equal=Grace"

    name_contains_not_A = Filter("Name", "A", "contains_not")
    assert name_contains_not_A.query_string == "filter__Name__contains_not=A"


def test_rows_with_name_grace(table):
    name_equal_grace = Filter("Name", "Grace")
    rows_with_name_grace = table.get_rows(filters=[name_equal_grace])
    for row in rows_with_name_grace:
        assert row["Name"] == "Grace"


def test_rows_without_A(table):
    name_contains_not_A = Filter("Name", "A", "contains_not")
    rows_without_A = table.get_rows(filters=[name_contains_not_A])
    for row in rows_without_A:
        assert "A" not in row["Name"]


def test_rows_with_last_name_hopper(table):
    rows_with_last_name_hopper = table.get_rows(filters=[Filter("Last name", "Hopper")])
    for row in rows_with_last_name_hopper:
        assert row["Last name"] == "Hopper"


def test_rows_with_name_ada_or_grace(table):
    rows_with_name_ada_or_grace = table.get_rows(
        filters=[Filter("Name", "Ada"), Filter("Name", "Grace")], filter_type="OR"
    )
    for row in rows_with_name_ada_or_grace:
        assert row["Name"] in ["Ada", "Grace"]


def test_rows_with_name_ada_or_last_name_pascal(table):
    rows_with_name_ada_or_last_name_pascal = table.get_rows(
        filters=[Filter("Name", "Ada"), Filter("Last name", "Pascal")], filter_type="OR"
    )
    for row in rows_with_name_ada_or_last_name_pascal:
        assert row["Name"] == "Ada" or row["Last name"] == "Pascal"


def test_rows_sorted_by_name_ascending(table):
    rows_name_ascending = table.get_rows(order_by=["Name"])
    first_row = next(rows_name_ascending)
    assert first_row["Name"] == "Ada"
    assert first_row["Last name"] == "Lovelace"


def test_rows_sorted_by_name_descending(table):
    rows_descending = table.get_rows(order_by=["-Name"])
    first_row = next(rows_descending)
    assert first_row["Name"] == "Spot"
    assert first_row["Last name"] == "Dog"


def test_search_rows_with_canine(table):
    # get rows with search
    rows_with_test = table.get_rows(search="canine")

    # Extract the first row (assuming there's at least one result)
    first_row = next(iter(rows_with_test), None)

    # Assert that the values in the row match the expected values
    assert first_row is not None, "No rows returned with search='canine'"
    assert (
        first_row["Name"] == "Spot"
    ), f"Expected Name: Spot, but got {first_row['Name']}"
    assert (
        first_row["Last name"] == "Dog"
    ), f"Expected Last name: Dog, but got {first_row['Last name']}"


def test_get_rows_from_view(table, baserow_config):
    # Get rows from view
    rows_from_view = table.get_rows(view_id=baserow_config["view_id"])

    # Ensure there are results
    assert rows_from_view, "No rows returned from view."

    # Check if the "Spot" row is present
    for row in rows_from_view:
        if row["Name"] == "Spot" and row["Last name"] == "Dog":
            break
    else:
        pytest.fail(
            "Expected row with Name: Spot and Last name: Dog not found in the view results."
        )


def test_get_rows_with_include(table):
    # Get rows with include parameters
    rows_with_include = table.get_rows(include=["Name", "Last name", "Notes", "Active"])

    # Get the first row from the RowIterator
    first_row = next(iter(rows_with_include))

    # Check the first row's content to ensure only the specified fields are present
    assert set(first_row.content.keys()) == {
        "Name",
        "Last name",
        "Notes",
        "Active",
    }, "Expected fields not present or additional fields present in the row content."


def test_get_rows_with_exclude(table):
    # Get rows with exclude parameters
    rows_with_exclude = table.get_rows(exclude=["Notes", "Active"])

    # Get the first row from the RowIterator
    first_row = next(iter(rows_with_exclude))

    # Check the first row's content to ensure the excluded fields are not present
    excluded_fields = {"Notes", "Active"}
    assert not (
        excluded_fields & first_row.content.keys()
    ), "Excluded fields are present in the row content."


@pytest.fixture
def added_row_fixture(table, baserow_config):
    new_row_data = {
        "Name": "Ringo",
        "Last name": "Staar",
        "Notes": "drums",
        "Active": True,
    }
    added_row = table.add_row(new_row_data)
    yield added_row  # This is the value that tests using this fixture will get.

    # Cleanup
    try:
        # If the row was not deleted in the test, try to delete it here.
        added_row.delete()
    except Exception as e:
        # just pass
        pass


def test_add_new_row_from_dict(added_row_fixture):
    # Check the data of the added row
    assert (
        added_row_fixture["Name"] == "Ringo"
    ), "Added row Name doesn't match expected value."
    assert (
        added_row_fixture["Last name"] == "Staar"
    ), "Added row Last Name doesn't match expected value."


def test_delete_added_row(added_row_fixture):
    # Delete the added row and check the status
    deleted_status = added_row_fixture.delete()
    assert deleted_status is True, "Row was not deleted successfully."


@pytest.fixture
def added_multiple_rows_fixture(table):
    add_multiple_row_data = [
        {
            "Name": "Nick",
            "Last name": "Saban",
            "Notes": "Head coach of Alabama Crimson Tide",
            "Active": True,
        },
        {
            "Name": "Dabo",
            "Last name": "Swinney",
            "Notes": "Head coach of Clemson Tigers",
            "Active": True,
        },
        {
            "Name": "Urban",
            "Last name": "Meyer",
            "Notes": "Former head coach of Ohio State Buckeyes",
            "Active": False,
        },
    ]

    added_rows = table.add_row(add_multiple_row_data)
    yield added_rows

    # Cleanup
    try:
        table.delete_rows(added_rows)
    except Exception:
        pass


def test_add_multiple_rows_from_list_of_dicts(added_multiple_rows_fixture):
    assert len(added_multiple_rows_fixture) == 3
    assert added_multiple_rows_fixture[0]["Name"] == "Nick"


def test_delete_multiple_rows(table, added_multiple_rows_fixture):
    deleted_status = table.delete_rows(added_multiple_rows_fixture)
    assert deleted_status == True


def test_delete_multiple_rows_by_ids(table, added_multiple_rows_fixture):
    rows_to_delete = [row.id for row in added_multiple_rows_fixture]

    delete_status = table.delete_rows(rows_to_delete)

    assert delete_status is True


def test_update_rows_from_dict(table):
    update_rows_data = [
        {"id": 3, "Notes": "dict update test"},
        {"id": 4, "Notes": "dict update test"},
        {"id": 5, "Notes": "dict update test"},
    ]
    updated_rows = table.update_rows(update_rows_data)

    # Ensure three rows were returned
    assert len(updated_rows) == 3

    # Check the "Notes" value for the first row
    assert updated_rows[0]["Notes"] == "dict update test"


def test_update_rows_from_row_objects(table):
    # Retrieve rows based on the filter condition
    my_rows = list(table.get_rows(filters=[Filter("Notes", "dict update test")]))

    # Update the rows in memory
    for row in my_rows:
        row.update(values={"Notes": "Row object update test"}, memory_only=True)

    # Update the rows in the table
    updated_rows = table.update_rows(my_rows)

    # Ensure three rows were returned
    assert len(updated_rows) == 3

    # Check the "Notes" value for the first row
    assert updated_rows[0]["Notes"] == "Row object update test"


def test_get_rows_with_non_matching_filter(table):
    # Attempt to retrieve a single row based on a non-matching filter
    single_row = table.get_rows(
        filters=[Filter("Notes", "asdfjkl;")], return_single=True
    )

    # Ensure no rows were found with the given criteria
    assert single_row is None, "A row was found but none were expected."


def test_get_single_row(table):
    # Attempt to retrieve a single row without any filters
    single_row = table.get_rows(return_single=True)

    # Ensure that a row was returned and it's of the correct type
    assert single_row is not None, "No row was returned but one was expected."
    assert isinstance(
        single_row, Row
    ), f"Expected a Row object, but got {type(single_row)}."


def test_set_value_in_memory_for_single_row(table):
    # Retrieve a single row without any filters
    single_row = table.get_rows(return_single=True)

    # Ensure that a row was returned and it's of the correct type
    assert single_row is not None, "No row was returned but one was expected."
    assert isinstance(
        single_row, Row
    ), f"Expected a Row object, but got {type(single_row)}."

    # Change the value in memory
    single_row["Notes"] = "Changed note in memory"

    # Check that the in-memory value of the row has changed
    assert (
        single_row["Notes"] == "Changed note in memory"
    ), "The in-memory value of the row did not change as expected."


def test_update_row_with_current_values(table):
    # Retrieve a single row with the specified filter
    single_row = table.get_rows(filters=[Filter("Name", "Blaise")], return_single=True)

    # Ensure that a row was returned and it's of the correct type
    assert single_row is not None, "No row was returned but one was expected."
    assert isinstance(
        single_row, Row
    ), f"Expected a Row object, but got {type(single_row)}."

    # Change the value in memory
    single_row["Notes"] = "Updated test note"

    # Update the row with its current in-memory values
    updated_row = single_row.update()

    # Ensure that the returned row from the update operation is of the correct type
    assert isinstance(
        updated_row, Row
    ), f"Expected a Row object from the update operation, but got {type(updated_row)}."

    # Check that the updated row has the expected values
    assert (
        updated_row["Name"] == "Blaise"
    ), f"Expected 'Blaise' for 'Name', but got {updated_row['Name']}."
    assert (
        updated_row["Notes"] == "Updated test note"
    ), f"Expected 'Updated test note' for 'Notes', but got {updated_row['Notes']}."


def test_update_row_with_dictionary(table):
    # Retrieve a single row with the specified filter
    single_row = table.get_rows(filters=[Filter("Name", "Blaise")], return_single=True)

    # Ensure that a row was returned and it's of the correct type
    assert single_row is not None, "No row was returned but one was expected."
    assert isinstance(
        single_row, Row
    ), f"Expected a Row object, but got {type(single_row)}."

    # Update the row using a dictionary
    updated_row = single_row.update({"Notes": "Updated row via dictionary"})

    # Ensure that the returned row from the update operation is of the correct type
    assert isinstance(
        updated_row, Row
    ), f"Expected a Row object from the update operation, but got {type(updated_row)}."

    # Check that the updated row has the expected values
    assert (
        updated_row["Name"] == "Blaise"
    ), f"Expected 'Blaise' for 'Name', but got {updated_row['Name']}."
    assert (
        updated_row["Notes"] == "Updated row via dictionary"
    ), f"Expected 'Updated row via dictionary' for 'Notes', but got {updated_row['Notes']}."
