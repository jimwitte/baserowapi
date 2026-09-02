from unittest.mock import Mock

import pytest

from baserowapi.exceptions import FieldDataRetrievalError, FieldValueError
from baserowapi.models.row import Row
from baserowapi.models.table import Table


pytestmark = pytest.mark.offline


def test_table_fields_are_schema_ordered_and_shallowly_read_only():
    client = Mock()
    client.make_api_request.return_value = [
        {"id": 2, "name": "Second", "type": "text", "order": 2},
        {"id": 1, "name": "First", "type": "text", "order": 1},
    ]
    table = Table(10, client)

    assert list(table.fields) == ["First", "Second"]
    assert [field.name for field in table.fields.values()] == ["First", "Second"]
    with pytest.raises(TypeError):
        table.fields["Third"] = table.fields["First"]


def test_duplicate_field_names_are_not_silently_collapsed():
    client = Mock()
    client.make_api_request.return_value = [
        {"id": 1, "name": "Duplicate", "type": "text", "order": 1},
        {"id": 2, "name": "Duplicate", "type": "text", "order": 2},
    ]

    with pytest.raises(FieldDataRetrievalError):
        Table(10, client).fields


def test_row_item_access_decodes_only_the_requested_field(characterized_table):
    row = Row(
        row_data={"id": 1, "Name": "safe", "Files": [{}]},
        table=characterized_table,
        client=characterized_table.client,
    )

    assert row["Name"] == "safe"
    with pytest.raises(FieldValueError):
        row["Files"]
    with pytest.raises(FieldValueError):
        _ = row.values


def test_row_mappings_are_shallowly_read_only_and_to_dict_is_a_copy(
    characterized_row,
):
    with pytest.raises(TypeError):
        characterized_row.raw_values["Name"] = "changed"
    with pytest.raises(TypeError):
        characterized_row.values["Name"] = "changed"

    copied = characterized_row.to_dict()
    copied["Name"] = "changed"
    assert characterized_row["Name"] == "Example"


def test_row_update_requires_an_explicit_mapping(characterized_row):
    with pytest.raises(TypeError):
        characterized_row.update()
