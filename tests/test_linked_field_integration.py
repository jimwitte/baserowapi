import pytest

from baserowapi import LinkedRow

pytestmark = pytest.mark.integration


def test_table_link_field_get_linked_rows(all_fields_table):
    linked_rows = all_fields_table.fields["TableLink"].get_linked_rows()

    assert [row.value for row in linked_rows] == ["fred", "neil", "geddy", "alex"]
    assert all(isinstance(row, LinkedRow) for row in linked_rows)
    assert all(isinstance(row.id, int) for row in linked_rows)


def test_update_table_link_field_with_discovered_rows(all_fields_table):
    created_row = all_fields_table.add_rows(
        [{"Name": "Test Row", "TableLink": []}]
    )[0]
    available_rows = all_fields_table.fields["TableLink"].get_linked_rows()
    assert len(available_rows) >= 2
    selected_rows = available_rows[:2]

    created_row.update({"TableLink": selected_rows})

    updated_rows = all_fields_table.get_row(created_row.id)["TableLink"]
    assert updated_rows == selected_rows
