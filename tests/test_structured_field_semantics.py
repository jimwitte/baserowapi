from collections.abc import Mapping
from unittest.mock import MagicMock, Mock

import pytest

from baserowapi import Baserow
from baserowapi.exceptions import FieldValidationError, FieldValueError
from baserowapi.models.fields import (
    FileField,
    LookupField,
    MultipleCollaboratorsField,
    MultipleSelectField,
    SingleSelectField,
    TableLinkField,
)
from baserowapi.models.values import (
    BaserowFile,
    Collaborator,
    LinkedRow,
    LookupEntry,
    SelectOption,
)


pytestmark = pytest.mark.offline


def select_metadata(options=None):
    return {
        "id": 1,
        "table_id": 10,
        "type": "single_select",
        "select_options": options
        or [{"id": 101, "value": "Open", "color": "green", "extra": True}],
    }


def test_domain_records_are_plain_records_not_mapping_substitutes():
    records = [
        SelectOption(1, "Open"),
        LinkedRow(10, 2, "Row"),
        BaserowFile("stored.txt"),
        Collaborator(3, "User"),
        LookupEntry(2, "value"),
    ]

    assert all(not isinstance(record, Mapping) for record in records)
    assert SelectOption(1, "Open") != "Open"
    assert LinkedRow(10, 2, "Row") != "Row"


def test_single_select_preserves_identity_metadata_and_encodes_write_forms():
    field = SingleSelectField("Status", select_metadata())
    option = field.decode_value(
        {"id": 101, "value": "Open", "color": "green", "extra": True}
    )

    assert option == SelectOption(101, "Open", "green")
    assert option.raw["extra"] is True
    assert field.options[0].raw["extra"] is True
    assert field.encode_value(option) == 101
    assert field.encode_value({"id": 101, "value": "Open"}) == 101
    assert field.encode_value(101) == 101
    assert field.encode_value("Open") == "Open"
    assert field.encode_value(None) is None


def test_select_strict_resolution_rejects_missing_and_duplicate_labels():
    field = SingleSelectField(
        "Status",
        select_metadata(
            [
                {"id": 101, "value": "Same", "color": "green"},
                {"id": 102, "value": "Same", "color": "red"},
            ]
        ),
    )

    with pytest.raises(FieldValidationError, match="ambiguous"):
        field.resolve_option("Same")
    with pytest.raises(FieldValidationError, match="No option"):
        field.resolve_option("Missing")


def test_multiple_select_preserves_identity_and_documented_write_shapes():
    metadata = select_metadata()
    metadata["type"] = "multiple_select"
    field = MultipleSelectField("Tags", metadata)

    assert field.decode_value([{"id": 101, "value": "Open", "color": "green"}]) == [
        SelectOption(101, "Open", "green")
    ]
    assert field.encode_value([SelectOption(101, "Open")]) == [101]
    assert field.encode_value([{"id": 101, "value": "Open"}]) == [101]
    assert field.encode_value([101, "Open"]) == [101, "Open"]
    assert field.encode_value("Open, Closed") == "Open, Closed"
    assert field.encode_value([]) == []
    with pytest.raises(FieldValidationError):
        field.encode_value(None)


def link_field(client=None, view_id=99):
    return TableLinkField(
        "Related",
        {
            "id": 7,
            "table_id": 10,
            "type": "link_row",
            "link_row_table_id": 20,
            "link_row_related_field_id": 8,
            "link_row_limit_selection_view_id": view_id,
        },
        client,
    )


def test_link_field_preserves_table_and_row_identity_and_encodes_write_forms():
    field = link_field()
    linked = field.decode_value([{"id": 501, "value": "Acme", "extra": True}])[0]

    assert linked == LinkedRow(20, 501, "Acme")
    assert linked.raw["extra"] is True
    assert field.encode_value([linked]) == [501]
    assert field.encode_value({"id": 501, "value": "Acme"}) == [501]
    assert field.encode_value(501) == 501
    assert field.encode_value("Acme") == "Acme"
    assert field.encode_value("Acme, Beta") == "Acme, Beta"
    assert field.encode_value([]) == []
    with pytest.raises(FieldValidationError):
        field.encode_value(None)


def test_linked_row_discovery_keeps_ids_and_honors_selection_view():
    client = Mock()
    table = Mock()
    table.id = 20
    table.primary_field = "Name"
    first = MagicMock(id=501)
    first.__getitem__.return_value = "Acme"
    second = MagicMock(id=502)
    second.__getitem__.return_value = "Acme"
    table.get_rows.return_value = [first, second]
    client.get_table.return_value = table
    field = link_field(client)

    rows = field.get_linked_rows()

    assert rows == [LinkedRow(20, 501, "Acme"), LinkedRow(20, 502, "Acme")]
    client.get_table.assert_called_once_with(20)
    table.get_rows.assert_called_once_with(include=["Name"], view_id=99)
    with pytest.raises(FieldValidationError, match="ambiguous"):
        field.resolve_linked_row("Acme")
    with pytest.raises(FieldValidationError, match="No linked row"):
        field.resolve_linked_row("Missing")


def test_file_field_preserves_object_metadata_and_encodes_names():
    field = FileField("Files", {"id": 8, "table_id": 10, "type": "file"})
    raw = {
        "name": "stored.png",
        "visible_name": "example.png",
        "url": "https://example.invalid/stored.png",
        "size": 42,
        "mime_type": "image/png",
        "original_name": "source.png",
        "extra": True,
    }
    uploaded = field.decode_value([raw])[0]

    assert uploaded == BaserowFile(
        "stored.png",
        "example.png",
        "https://example.invalid/stored.png",
        42,
        "image/png",
        "source.png",
    )
    assert uploaded.raw["extra"] is True
    assert field.encode_value([uploaded, raw, "other.png"]) == [
        "stored.png",
        "stored.png",
        "other.png",
    ]
    assert field.encode_value("stored.png, other.png") == "stored.png, other.png"
    assert field.encode_value(None) is None


def test_collaborator_and_lookup_results_preserve_identity_and_raw_values():
    collaborator_field = MultipleCollaboratorsField(
        "Collaborators",
        {"id": 12, "table_id": 10, "type": "multiple_collaborators"},
    )
    collaborator = collaborator_field.decode_value(
        [{"id": 701, "name": "Example", "email": "e@example.invalid", "extra": True}]
    )[0]

    assert collaborator == Collaborator(701, "Example", "e@example.invalid")
    assert collaborator.raw["extra"] is True
    assert collaborator_field.encode_value([collaborator, {"id": 702}]) == [
        {"id": 701},
        {"id": 702},
    ]

    lookup_field = LookupField(
        "Lookup",
        {"id": 11, "table_id": 10, "type": "lookup", "read_only": True},
    )
    nested_value = {"id": 101, "value": "Open"}
    lookup = lookup_field.decode_value([{"id": 501, "value": nested_value}])[0]

    assert lookup == LookupEntry(501, nested_value)
    assert lookup.value is nested_value
    assert lookup.raw == {"id": 501, "value": nested_value}


def test_invalid_structured_response_shapes_raise_field_value_errors():
    with pytest.raises(FieldValueError):
        FileField("Files", {"id": 8, "type": "file"}).decode_value([{}])
    with pytest.raises(FieldValueError):
        link_field().decode_value([True])


def test_client_file_uploads_return_unattached_file_records(tmp_path):
    path = tmp_path / "example.txt"
    path.write_text("example", encoding="utf-8")
    client = Baserow(token="test")
    client.make_api_request = Mock(
        return_value={
            "name": "stored.txt",
            "visible_name": "example.txt",
            "url": "https://example.invalid/stored.txt",
            "size": 7,
            "mime_type": "text/plain",
            "original_name": "example.txt",
        }
    )

    uploaded = client.upload_file(path)

    assert uploaded == BaserowFile(
        "stored.txt",
        "example.txt",
        "https://example.invalid/stored.txt",
        7,
        "text/plain",
        "example.txt",
    )
    assert uploaded.raw["name"] == "stored.txt"
    assert uploaded.original_name == "example.txt"
    client.make_api_request.assert_called_once()

    imported = client.upload_file_via_url(uploaded.url)
    assert imported.name == "stored.txt"
    assert client.make_api_request.call_args.kwargs["data"] == {"url": uploaded.url}
