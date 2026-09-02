import pytest


pytestmark = pytest.mark.integration


def test_hosted_singular_and_batch_writes_apply_the_same_field_semantics(
    all_fields_table,
):
    values = {
        "Name": "phase-5-singular",
        "US Date Time": "2026-09-02T12:30:00+00:00",
        "SingleSelect": "option 1",
        "MultipleSelect": ["option 1", "option 2"],
        "FileField": [],
    }
    singular = all_fields_table.add_row(values)
    batch = all_fields_table.add_rows([{**values, "Name": "phase-5-batch"}])[0]

    assert singular["US Date Time"] == batch["US Date Time"]
    assert singular["SingleSelect"].value == batch["SingleSelect"].value
    assert [option.value for option in singular["MultipleSelect"]] == [
        option.value for option in batch["MultipleSelect"]
    ]
    assert singular["FileField"] == batch["FileField"] == []

    updated_singular = all_fields_table.update_row(
        singular.id,
        {
            "US Date Time": "2026-09-02T13:30:00+00:00",
            "SingleSelect": singular["SingleSelect"],
        },
    )
    updated_batch = all_fields_table.update_rows(
        [
            {
                "id": batch.id,
                "US Date Time": "2026-09-02T13:30:00+00:00",
                "SingleSelect": batch["SingleSelect"],
            }
        ]
    )[0]

    assert updated_singular["US Date Time"] == updated_batch["US Date Time"]
    assert updated_singular["SingleSelect"].id == updated_batch["SingleSelect"].id


def test_hosted_schema_blocks_computed_and_absent_fields_before_write(
    all_fields_table,
):
    with pytest.raises(KeyError, match="read-only"):
        all_fields_table.add_row({"Name": "blocked", "Formula": "computed"})
    with pytest.raises(KeyError, match="does not exist"):
        all_fields_table.add_row({"Not a hosted field": "unknown"})


def test_hosted_password_read_states_and_accepted_write_forms(all_fields_table):
    row = all_fields_table.add_row(
        {"Name": "phase-6-password-semantics", "Password": "temporary-password"}
    )
    assert row.raw_values["Password"] is True
    assert row["Password"] is True

    preserved = all_fields_table.update_row(row.id, {"Password": True})
    assert preserved.raw_values["Password"] is True

    cleared = all_fields_table.update_row(row.id, {"Password": None})
    assert cleared.raw_values["Password"] is None
    assert cleared["Password"] is None
