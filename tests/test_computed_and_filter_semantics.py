from uuid import UUID

import pytest

import baserowapi
from baserowapi import Filter, FilterCompatibility
from baserowapi.exceptions import FieldValueError
from baserowapi.models.fields import (
    AutonumberField,
    CountField,
    GenericField,
    NumberField,
    UUIDField,
)


pytestmark = pytest.mark.offline


def test_computed_result_metadata_and_evidenced_shapes_are_preserved(
    characterized_row,
):
    formula_field = characterized_row.table.fields["Formula"]
    count_field = characterized_row.table.fields["Count"]
    lookup_field = characterized_row.table.fields["Lookup"]

    button = characterized_row["Formula"]
    assert formula_field.formula_type == "button"
    assert button == {"label": "Baserow Home", "url": "https://baserow.io"}
    assert isinstance(count_field, NumberField)
    assert count_field.formula_type == "number"
    assert characterized_row["Count"] == "1"
    assert lookup_field.formula_type == "array"
    assert lookup_field.array_formula_type == "text"
    assert characterized_row["Lookup"][0].value == "Acme"


def test_unknown_computed_shapes_remain_raw():
    raw_formula = {"future_result": [1, 2]}
    formula_field = baserowapi.FormulaField(
        "Future formula",
        {
            "id": 1,
            "type": "formula",
            "formula_type": "future_result_type",
            "read_only": True,
        },
    )
    assert formula_field.decode_value(raw_formula) is raw_formula

    raw_lookup_value = {"future": "shape"}
    lookup_field = baserowapi.LookupField(
        "Future lookup",
        {
            "id": 2,
            "type": "lookup",
            "formula_type": "array",
            "array_formula_type": "future_result_type",
            "read_only": True,
        },
    )
    entry = lookup_field.decode_value(
        [{"id": 10, "value": raw_lookup_value, "extra": True}]
    )[0]
    assert entry.value is raw_lookup_value
    assert entry.raw["extra"] is True


def test_uuid_and_autonumber_fields_encode_hosted_read_only_knowledge(
    characterized_table,
):
    uuid_field = characterized_table.fields["UUID"]
    autonumber_field = characterized_table.fields["Autonumber"]

    assert isinstance(uuid_field, UUIDField)
    assert isinstance(autonumber_field, AutonumberField)
    assert uuid_field.is_read_only
    assert autonumber_field.is_read_only
    assert uuid_field.parse_value(
        "123e4567-e89b-12d3-a456-426614174000"
    ) == UUID("123e4567-e89b-12d3-a456-426614174000")
    with pytest.raises(FieldValueError):
        uuid_field.parse_value("not-a-uuid")


def test_filter_compatibility_is_advisory_and_three_state(characterized_table):
    text_field = characterized_table.fields["Name"]
    assert (
        text_field.filter_compatibility("starts_with")
        is FilterCompatibility.SUPPORTED
    )
    assert (
        text_field.filter_compatibility("date_is")
        is FilterCompatibility.UNSUPPORTED
    )
    assert (
        text_field.filter_compatibility("future_hosted_operator")
        is FilterCompatibility.UNKNOWN
    )

    unknown_field = GenericField(
        "Future", {"id": 99, "type": "future_type", "read_only": False}
    )
    assert (
        unknown_field.filter_compatibility("equal")
        is FilterCompatibility.UNKNOWN
    )


def test_filter_has_one_json_tree_encoding_and_unknown_operators_pass_through(
    characterized_table,
):
    filter_object = Filter("Name", "Example", "future_hosted_operator")
    assert not hasattr(filter_object, "query_string")

    tree = characterized_table._construct_filter_tree([filter_object], "AND")
    assert tree == {
        "filter_type": "AND",
        "filters": [
            {
                "field": "Name",
                "type": "future_hosted_operator",
                "value": "Example",
            }
        ],
        "groups": [],
    }


def test_detached_filter_validator_is_no_longer_public():
    assert not hasattr(baserowapi, "FilterValidator")


def test_all_write_paths_exclude_read_only_fields(
    characterized_table, characterized_row, characterized_row_response
):
    read_only_names = {"Formula", "Count", "Lookup", "UUID", "Autonumber"}

    with pytest.raises(KeyError):
        characterized_table.add_row({"Name": "New", "Formula": "not writable"})
    with pytest.raises(KeyError):
        characterized_row.update({"Count": "2"})
    with pytest.raises(KeyError):
        characterized_table.update_rows(
            [{"id": characterized_row.id, "UUID": "not writable"}]
        )

    characterized_table.client.make_api_request.return_value = {
        "items": [characterized_row_response]
    }
    characterized_table.update_rows([characterized_row])
    payload = characterized_table.client.make_api_request.call_args.kwargs["data"]
    assert read_only_names.isdisjoint(payload["items"][0])
