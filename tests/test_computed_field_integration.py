import pytest

from baserowapi import AutonumberField, Filter, UUIDField


pytestmark = pytest.mark.integration


def test_hosted_computed_uuid_autonumber_shapes_and_filters(all_fields_table):
    row = all_fields_table.add_row({"Name": "phase-4-hosted-semantics"})
    fetched = all_fields_table.get_row(row.id)

    assert fetched["Formula"] == {
        "label": "Baserow Home",
        "url": "https://baserow.io",
    }
    assert fetched["Count"] == "0"
    assert fetched["Lookup"] == []
    assert isinstance(fetched["UUID"], str)
    assert isinstance(fetched["Autonumber"], int)
    assert isinstance(all_fields_table.fields["UUID"], UUIDField)
    assert isinstance(all_fields_table.fields["Autonumber"], AutonumberField)

    filters = [
        Filter("UUID", fetched["UUID"], "equal"),
        Filter("Autonumber", fetched["Autonumber"], "equal"),
        Filter("Count", "0", "equal"),
        Filter("Lookup", "", "empty"),
    ]
    for filter_object in filters:
        matching_ids = {
            result.id for result in all_fields_table.get_rows(filters=[filter_object])
        }
        assert fetched.id in matching_ids, filter_object.field_name
