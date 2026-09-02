from datetime import datetime, timezone

import pytest

from baserowapi.exceptions import FieldValidationError
from baserowapi.models.fields import GenericField


pytestmark = pytest.mark.offline


def test_current_scalar_reads_preserve_baserow_strings(characterized_row):
    assert characterized_row["Number"] == "42.00"
    assert characterized_row["Date Only"] == "2026-09-01"
    assert characterized_row["Date Time"] == "2026-09-01T12:30:00Z"


def test_current_structured_reads_discard_some_identity(characterized_row):
    assert characterized_row["Status"] == "Open"
    assert characterized_row["Tags"] == ["Urgent", "Customer"]
    assert characterized_row["Related"] == ["Acme"]
    assert characterized_row["Lookup"] == ["Acme"]

    assert characterized_row.values["Status"]._raw_value["id"] == 101
    assert characterized_row.values["Related"]._raw_value[0]["id"] == 501
    assert characterized_row.values["Lookup"]._raw_value[0]["id"] == 501


def test_current_file_and_collaborator_reads_preserve_raw_objects(characterized_row):
    assert characterized_row["Files"][0]["name"] == "hashed-name.png"
    assert characterized_row["Files"][0]["visible_name"] == "example.png"
    assert characterized_row["Collaborators"] == [
        {
            "id": 701,
            "name": "Example User",
            "email": "user@example.invalid",
        }
    ]


def test_current_computed_and_password_reads(characterized_row):
    assert characterized_row["Formula"] == "Example"
    assert characterized_row["Count"] == "1"
    assert characterized_row["Password"] is True


def test_unknown_fields_retain_type_metadata_and_raw_value(characterized_row):
    field = characterized_row.table.fields["Future Value"]

    assert isinstance(field, GenericField)
    assert field.type == "future_type"
    assert field.field_data["future_setting"] == "preserve-me"
    assert characterized_row["Future Value"] == {"new": "shape"}


def test_uuid_and_autonumber_currently_use_generic_fallback(characterized_row):
    assert isinstance(characterized_row.table.fields["UUID"], GenericField)
    assert isinstance(characterized_row.table.fields["Autonumber"], GenericField)
    assert characterized_row["UUID"] == "123e4567-e89b-12d3-a456-426614174000"
    assert characterized_row["Autonumber"] == 12


def test_current_date_helpers_parse_iso_values(characterized_row):
    assert characterized_row.values["Date Only"].as_datetime() == datetime(
        2026, 9, 1
    )
    assert characterized_row.values["Date Time"].as_datetime() == datetime(
        2026, 9, 1, 12, 30, tzinfo=timezone.utc
    )


def test_date_encoder_does_not_guess_missing_information(characterized_table):
    with pytest.raises(FieldValidationError):
        characterized_table.fields["Date Only"].format_for_api("26/9/1")
    with pytest.raises(FieldValidationError):
        characterized_table.fields["Date Time"].format_for_api("2026-09-01")


def test_current_row_dictionary_contains_decoded_values_only(characterized_row):
    values = characterized_row.to_dict()

    assert "id" not in values
    assert "order" not in values
    assert values["Status"] == "Open"
    assert values["Related"] == ["Acme"]


def test_current_custom_containers_iterate_over_objects(characterized_row):
    assert next(iter(characterized_row.table.fields)).name == "Name"
    assert characterized_row.table.fields["Name"].name == "Name"
    assert "Name" in characterized_row.table.fields
    assert next(iter(characterized_row.values)).name == "Name"
    assert characterized_row.values.fields[0] == "Name"


def test_current_item_assignment_stages_a_value_without_a_request(characterized_row):
    characterized_row["Name"] = "Changed"

    assert characterized_row["Name"] == "Changed"
    assert characterized_row.to_dict()["Name"] == "Changed"
    characterized_row.client.make_api_request.assert_not_called()
