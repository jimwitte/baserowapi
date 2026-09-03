from datetime import date, datetime, timedelta, timezone
import logging

import pytest

from baserowapi.exceptions import FieldValidationError, FieldValueError
from baserowapi.models.fields import GenericField, PhoneNumberField


pytestmark = pytest.mark.offline


def test_scalar_fields_decode_baserow_values_without_changing_representation(
    characterized_table,
):
    assert characterized_table.fields["Name"].decode_value("Example") == "Example"
    assert characterized_table.fields["Active"].decode_value(True) is True
    assert characterized_table.fields["Rating"].decode_value(4) == 4
    assert characterized_table.fields["Number"].decode_value("42.00") == "42.00"
    assert (
        characterized_table.fields["Date Time"].decode_value(
            "2026-09-01T12:30:00Z"
        )
        == "2026-09-01T12:30:00Z"
    )


def test_unknown_field_operations_are_lossless_and_quiet(caplog):
    raw_value = {"new": ["shape"]}
    field_data = {
        "id": 99,
        "table_id": 10,
        "name": "Future",
        "type": "future_type",
        "future_setting": "preserve-me",
    }

    with caplog.at_level(logging.WARNING):
        field = GenericField("Future", field_data)
        assert field.decode_value(raw_value) is raw_value
        assert field.encode_value(raw_value) is raw_value

    assert field.type == "future_type"
    assert field.field_data is field_data
    assert caplog.records == []


def test_invalid_phone_number_is_not_repeated_in_diagnostics(caplog):
    sentinel = "PRIVATE_PHONE_VALUE"
    field = PhoneNumberField(
        "Phone", {"id": 1, "name": "Phone", "type": "phone_number", "order": 0}
    )

    with caplog.at_level(logging.ERROR):
        with pytest.raises(FieldValidationError) as raised:
            field.encode_value(sentinel)

    assert sentinel not in str(raised.value)
    assert sentinel not in caplog.text


@pytest.mark.parametrize("value", [0, 42, -1, 1.25, "42.00", None])
def test_number_field_accepts_hosted_write_forms(characterized_table, value):
    field = characterized_table.fields["Number"]

    assert field.encode_value(value) == value
    assert field.format_for_api(value) == value


@pytest.mark.parametrize("value", [True, "not-a-number", "1.234", float("inf")])
def test_number_field_rejects_values_hosted_baserow_rejects(
    characterized_table, value
):
    with pytest.raises(FieldValidationError):
        characterized_table.fields["Number"].encode_value(value)


def test_boolean_and_rating_nullability_matches_hosted_baserow(characterized_table):
    with pytest.raises(FieldValidationError):
        characterized_table.fields["Active"].encode_value(None)
    with pytest.raises(FieldValidationError):
        characterized_table.fields["Rating"].encode_value(None)


def test_password_field_preserves_wire_state_and_rejects_malformed_reads(
    characterized_table,
):
    field = characterized_table.fields["Password"]

    assert field.decode_value(True) is True
    assert field.decode_value(None) is None
    assert field.is_set(True) is True
    assert field.is_set(None) is False
    for malformed in (False, 1, "true"):
        with pytest.raises(FieldValueError):
            field.decode_value(malformed)


def test_rating_field_rejects_boolean_values(characterized_table):
    with pytest.raises(FieldValidationError):
        characterized_table.fields["Rating"].encode_value(True)


def test_date_fields_parse_explicit_iso_values(characterized_table):
    date_field = characterized_table.fields["Date Only"]
    datetime_field = characterized_table.fields["Date Time"]

    assert date_field.parse_value("2026-09-01") == date(2026, 9, 1)
    assert datetime_field.parse_value("2026-09-01T12:30:00Z") == datetime(
        2026, 9, 1, 12, 30, tzinfo=timezone.utc
    )


def test_date_fields_encode_typed_values_without_timezone_guessing(
    characterized_table,
):
    date_field = characterized_table.fields["Date Only"]
    datetime_field = characterized_table.fields["Date Time"]

    assert date_field.encode_value(date(2026, 9, 1)) == "2026-09-01"
    assert (
        datetime_field.encode_value(
            datetime(2026, 9, 1, 12, 30, tzinfo=timezone.utc)
        )
        == "2026-09-01T12:30:00Z"
    )
    assert (
        datetime_field.encode_value(
            datetime(
                2026,
                9,
                1,
                8,
                30,
                tzinfo=timezone(-timedelta(hours=4)),
            )
        )
        == "2026-09-01T08:30:00-04:00"
    )


@pytest.mark.parametrize("value", ["26/9/1", "2026-9-1", "2026-09-01T12:00:00Z"])
def test_date_only_field_rejects_ambiguous_or_datetime_values(
    characterized_table, value
):
    with pytest.raises(FieldValidationError):
        characterized_table.fields["Date Only"].encode_value(value)


@pytest.mark.parametrize(
    "value",
    ["2026-09-01", "2026-09-01T12:00:00", datetime(2026, 9, 1, 12)],
)
def test_datetime_field_requires_time_and_explicit_timezone(
    characterized_table, value
):
    with pytest.raises(FieldValidationError):
        characterized_table.fields["Date Time"].encode_value(value)


def test_date_display_uses_field_timezone_metadata(characterized_table):
    field = characterized_table.fields["Date Time"]

    assert (
        field.format_value("2026-09-01T08:30:00-04:00")
        == "2026-09-01 12:30:00 UTC"
    )


def test_explicit_display_timezone_overrides_field_timezone(characterized_table):
    field = characterized_table.fields["Date Time"]

    assert (
        field.format_value(
            "2026-09-01T12:30:00Z", target_timezone="America/Chicago"
        )
        == "2026-09-01 07:30:00 CDT"
    )


def test_date_parse_helper_has_a_field_conversion_error(characterized_table):
    with pytest.raises(FieldValueError):
        characterized_table.fields["Date Time"].parse_value("2026-09-01")


def test_scalar_row_access_uses_field_semantics(characterized_row):
    assert characterized_row["Active"] is True
    assert characterized_row["Rating"] == 4
    assert characterized_row["Number"] == "42.00"
    assert (
        characterized_row.table.fields["Number"].encode_value("21.50")
        == "21.50"
    )
