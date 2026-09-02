from collections.abc import Mapping
from datetime import date, datetime, timezone

import pytest

from baserowapi.exceptions import FieldValidationError
from baserowapi.models.fields import AutonumberField, GenericField, UUIDField
from baserowapi.models.values import (
    BaserowFile,
    Collaborator,
    LinkedRow,
    LookupEntry,
    SelectOption,
)


pytestmark = pytest.mark.offline


def test_current_scalar_reads_preserve_baserow_strings(characterized_row):
    assert characterized_row["Number"] == "42.00"
    assert characterized_row["Date Only"] == "2026-09-01"
    assert characterized_row["Date Time"] == "2026-09-01T12:30:00Z"


def test_structured_reads_preserve_baserow_identity(characterized_row):
    assert characterized_row["Status"] == SelectOption(101, "Open", "green")
    assert characterized_row["Tags"] == [
        SelectOption(201, "Urgent", "red"),
        SelectOption(202, "Customer", "blue"),
    ]
    assert characterized_row["Related"] == [LinkedRow(20, 501, "Acme")]
    assert characterized_row["Lookup"] == [LookupEntry(501, "Acme")]

    assert characterized_row["Status"].raw["id"] == 101
    assert characterized_row["Related"][0].raw["id"] == 501
    assert characterized_row["Lookup"][0].raw["id"] == 501


def test_file_and_collaborator_reads_use_identity_records(characterized_row):
    assert isinstance(characterized_row["Files"][0], BaserowFile)
    assert characterized_row["Files"][0].name == "hashed-name.png"
    assert characterized_row["Files"][0].visible_name == "example.png"
    assert characterized_row["Collaborators"] == [
        Collaborator(701, "Example User", "user@example.invalid")
    ]


def test_current_computed_and_password_reads(characterized_row):
    assert characterized_row["Formula"] == {
        "label": "Baserow Home",
        "url": "https://baserow.io",
    }
    assert characterized_row["Count"] == "1"
    assert characterized_row["Password"] is True


def test_unknown_fields_retain_type_metadata_and_raw_value(characterized_row):
    field = characterized_row.table.fields["Future Value"]

    assert isinstance(field, GenericField)
    assert field.type == "future_type"
    assert field.field_data["future_setting"] == "preserve-me"
    assert characterized_row["Future Value"] == {"new": "shape"}


def test_uuid_and_autonumber_have_dedicated_read_only_fields(characterized_row):
    assert isinstance(characterized_row.table.fields["UUID"], UUIDField)
    assert isinstance(characterized_row.table.fields["Autonumber"], AutonumberField)
    assert characterized_row["UUID"] == "123e4567-e89b-12d3-a456-426614174000"
    assert characterized_row["Autonumber"] == 12


def test_current_date_helpers_parse_iso_values(characterized_row):
    assert characterized_row.table.fields["Date Only"].parse_value(
        characterized_row["Date Only"]
    ) == date(2026, 9, 1)
    assert characterized_row.table.fields["Date Time"].parse_value(
        characterized_row["Date Time"]
    ) == datetime(
        2026, 9, 1, 12, 30, tzinfo=timezone.utc
    )


def test_date_encoder_does_not_guess_missing_information(characterized_table):
    with pytest.raises(FieldValidationError):
        characterized_table.fields["Date Only"].format_for_api("26/9/1")
    with pytest.raises(FieldValidationError):
        characterized_table.fields["Date Time"].format_for_api("2026-09-01")


def test_row_dictionary_contains_decoded_values_only(characterized_row):
    values = characterized_row.to_dict()

    assert "id" not in values
    assert "order" not in values
    assert values["Status"] == SelectOption(101, "Open", "green")
    assert values["Related"] == [LinkedRow(20, 501, "Acme")]


def test_field_and_row_values_are_read_only_mappings(characterized_row):
    assert isinstance(characterized_row.table.fields, Mapping)
    assert next(iter(characterized_row.table.fields)) == "Name"
    assert characterized_row.table.fields["Name"].name == "Name"
    assert "Name" in characterized_row.table.fields
    assert next(iter(characterized_row.values)) == "Name"
    assert characterized_row.values["Name"] == "Example"
    with pytest.raises(TypeError):
        characterized_row.table.fields["new"] = object()
    with pytest.raises(TypeError):
        characterized_row.values["Name"] = "Changed"


def test_row_exposes_raw_values_without_staged_mutation(characterized_row):
    assert characterized_row.raw_values["Status"] == {
        "id": 101,
        "value": "Open",
        "color": "green",
    }
    assert characterized_row.values["Status"] == SelectOption(101, "Open", "green")

    with pytest.raises(TypeError):
        characterized_row["Name"] = "Changed"
    characterized_row.client.make_api_request.assert_not_called()


def test_password_field_preserves_hosted_state_and_has_explicit_helper(
    characterized_row,
):
    field = characterized_row.table.fields["Password"]

    assert characterized_row["Password"] is True
    assert field.is_set(characterized_row.raw_values["Password"])
    assert not field.is_set(None)
