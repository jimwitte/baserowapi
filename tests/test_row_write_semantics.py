from copy import deepcopy
from unittest.mock import Mock

import pytest

from baserowapi.exceptions import BaserowResponseError, RowAddError, RowUpdateError
from baserowapi.models.row import Row
from baserowapi.models.values import BaserowFile, LinkedRow


pytestmark = pytest.mark.offline


def representative_values(characterized_table):
    return {
        "Date Time": "2026-09-01T00:00:00+00:00",
        "Status": characterized_table.fields["Status"].options[0],
        "Tags": characterized_table.fields["Tags"].options,
        "Related": [LinkedRow(table_id=20, id=501, value="Acme")],
        "Files": [BaserowFile(name="stored-file.png")],
        "Future Value": {"future": [1, 2]},
    }


def expected_values():
    return {
        "Date Time": "2026-09-01T00:00:00Z",
        "Status": 101,
        "Tags": [201, 202],
        "Related": [501],
        "Files": ["stored-file.png"],
        "Future Value": {"future": [1, 2]},
    }


def test_singular_and_batch_create_use_identical_field_encoding(
    characterized_table, characterized_row_response
):
    characterized_table.client.make_api_request.side_effect = [
        deepcopy(characterized_row_response),
        {"items": [deepcopy(characterized_row_response)]},
    ]

    created = characterized_table.add_row(representative_values(characterized_table))
    created_many = characterized_table.add_rows(
        [representative_values(characterized_table)]
    )

    assert isinstance(created, Row)
    assert isinstance(created_many, list)
    assert characterized_table.client.make_api_request.call_args_list[0].kwargs[
        "data"
    ] == expected_values()
    assert characterized_table.client.make_api_request.call_args_list[1].kwargs[
        "data"
    ] == {"items": [expected_values()]}


def test_singular_and_batch_update_use_identical_field_encoding(
    characterized_table, characterized_row_response
):
    characterized_table.client.make_api_request.side_effect = [
        deepcopy(characterized_row_response),
        {"items": [deepcopy(characterized_row_response)]},
    ]

    characterized_table.update_row(
        "1001", representative_values(characterized_table)
    )
    characterized_table.update_rows(
        [{"id": "1001", **representative_values(characterized_table)}]
    )

    assert characterized_table.client.make_api_request.call_args_list[0].kwargs[
        "data"
    ] == expected_values()
    assert characterized_table.client.make_api_request.call_args_list[1].kwargs[
        "data"
    ] == {"items": [{"id": 1001, **expected_values()}]}


def test_batch_updates_require_explicit_mappings(characterized_table, characterized_row):
    with pytest.raises(TypeError, match="Expected a mapping"):
        characterized_table.update_rows([characterized_row])

    characterized_table.client.make_api_request.assert_not_called()


def test_row_update_is_a_thin_table_delegate(
    characterized_row, characterized_row_response
):
    updated = Row(
        row_data={**characterized_row_response, "Name": "Updated"},
        table=characterized_row.table,
        client=characterized_row.client,
    )
    characterized_row.table.update_row = Mock(return_value=updated)

    returned = characterized_row.update({"Name": "Updated"})

    assert returned is characterized_row
    characterized_row.table.update_row.assert_called_once_with(
        characterized_row_response["id"], {"Name": "Updated"}
    )
    assert characterized_row["Name"] == "Updated"


def test_all_rows_are_encoded_before_the_first_batch_request(characterized_table):
    with pytest.raises(KeyError, match="read-only"):
        characterized_table.add_rows(
            [{"Name": "valid"}, {"Name": "invalid", "Formula": "blocked"}],
            batch_size=1,
        )

    characterized_table.client.make_api_request.assert_not_called()


@pytest.mark.parametrize("batch_size", [0, -1])
def test_batch_size_must_be_positive(characterized_table, batch_size):
    with pytest.raises(ValueError, match="greater than zero"):
        characterized_table.add_rows([{"Name": "valid"}], batch_size=batch_size)


@pytest.mark.parametrize("batch_size", [True, 1.5, "2"])
def test_batch_size_must_be_an_integer(characterized_table, batch_size):
    with pytest.raises(TypeError, match="positive integer"):
        characterized_table.add_rows([{"Name": "valid"}], batch_size=batch_size)


@pytest.mark.parametrize("row_id", [0, -1, "0", "not-an-id"])
def test_row_id_must_be_positive(characterized_table, row_id):
    with pytest.raises(ValueError):
        characterized_table.update_row(row_id, {"Name": "valid"})


@pytest.mark.parametrize("row_id", [True, 1.5, None])
def test_row_id_must_be_an_integer_or_numeric_string(characterized_table, row_id):
    with pytest.raises(TypeError):
        characterized_table.update_row(row_id, {"Name": "valid"})


def test_plural_methods_reject_singular_mappings(characterized_table):
    with pytest.raises(TypeError, match="use add_row"):
        characterized_table.add_rows({"Name": "one"})
    with pytest.raises(TypeError, match="use update_row"):
        characterized_table.update_rows({"id": 1, "Name": "one"})


def test_batch_response_shape_and_count_are_validated(
    characterized_table, characterized_row_response
):
    characterized_table.client.make_api_request.return_value = {"items": []}

    with pytest.raises(RowAddError) as raised:
        characterized_table.add_rows([{"Name": "one"}])

    assert isinstance(raised.value.__cause__, BaserowResponseError)
    assert raised.value.failed_batch_number == 1


def test_partial_batch_failure_reports_completed_rows(
    characterized_table, characterized_row_response
):
    remote_error = RuntimeError("second batch failed")
    characterized_table.client.make_api_request.side_effect = [
        {"items": [deepcopy(characterized_row_response)]},
        remote_error,
    ]

    with pytest.raises(RowUpdateError) as raised:
        characterized_table.update_rows(
            [{"id": 1001, "Name": "one"}, {"id": 1002, "Name": "two"}],
            batch_size=1,
        )

    assert raised.value.failed_batch_number == 2
    assert raised.value.completed_count == 1
    assert raised.value.completed_row_ids == (1001,)
    assert raised.value.__cause__ is remote_error
