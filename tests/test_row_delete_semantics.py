from copy import deepcopy
from unittest.mock import Mock, call

import pytest

from baserowapi.exceptions import (
    BaserowResponseError,
    RowDeleteError,
    RowMoveError,
)
from baserowapi.models.row import Row


pytestmark = pytest.mark.offline


def test_batch_delete_requires_a_non_empty_list(characterized_table):
    for value in ((), iter([1]), {1}, {"id": 1}):
        with pytest.raises(TypeError, match="list"):
            characterized_table.delete_rows(value)

    with pytest.raises(ValueError, match="at least one"):
        characterized_table.delete_rows([])

    characterized_table.client.make_api_request.assert_not_called()


@pytest.mark.parametrize("row_id", [0, -1, "0", "not-an-id"])
def test_batch_delete_rejects_invalid_row_ids_before_request(
    characterized_table, row_id
):
    with pytest.raises(ValueError):
        characterized_table.delete_rows([1, row_id], batch_size=1)

    characterized_table.client.make_api_request.assert_not_called()


@pytest.mark.parametrize("row_id", [True, 1.5, None, Mock()])
def test_batch_delete_rejects_invalid_row_id_types_before_request(
    characterized_table, row_id
):
    with pytest.raises(TypeError):
        characterized_table.delete_rows([1, row_id], batch_size=1)

    characterized_table.client.make_api_request.assert_not_called()


@pytest.mark.parametrize("batch_size", [0, -1])
def test_batch_delete_rejects_non_positive_batch_sizes_before_request(
    characterized_table, batch_size
):
    with pytest.raises(ValueError):
        characterized_table.delete_rows([1], batch_size=batch_size)

    characterized_table.client.make_api_request.assert_not_called()


@pytest.mark.parametrize("batch_size", [True, 1.5, "2"])
def test_batch_delete_rejects_non_integer_batch_sizes_before_request(
    characterized_table, batch_size
):
    with pytest.raises(TypeError):
        characterized_table.delete_rows([1], batch_size=batch_size)

    characterized_table.client.make_api_request.assert_not_called()


def test_batch_delete_validates_then_sends_explicit_id_chunks(characterized_table):
    characterized_table.client.make_api_request.return_value = 204

    assert characterized_table.delete_rows(["1", 2, 3], batch_size=2) is True

    endpoint = "/api/database/rows/table/10/batch-delete/"
    assert characterized_table.client.make_api_request.call_args_list == [
        call(endpoint, method="POST", data={"items": [1, 2]}),
        call(endpoint, method="POST", data={"items": [3]}),
    ]


def test_partial_batch_delete_reports_confirmed_ids(characterized_table):
    remote_error = RuntimeError("second batch failed")
    characterized_table.client.make_api_request.side_effect = [204, remote_error]

    with pytest.raises(RowDeleteError) as raised:
        characterized_table.delete_rows([1, 2], batch_size=1)

    assert raised.value.failed_batch_number == 2
    assert raised.value.completed_count == 1
    assert raised.value.completed_row_ids == (1,)
    assert raised.value.__cause__ is remote_error


def test_batch_delete_does_not_confirm_an_unexpected_success_response(
    characterized_table,
):
    characterized_table.client.make_api_request.side_effect = [204, {}]

    with pytest.raises(RowDeleteError) as raised:
        characterized_table.delete_rows([1, 2], batch_size=1)

    assert raised.value.failed_batch_number == 2
    assert raised.value.completed_count == 1
    assert raised.value.completed_row_ids == (1,)
    assert isinstance(raised.value.__cause__, BaserowResponseError)


def test_single_delete_validates_and_uses_the_singular_endpoint(characterized_table):
    characterized_table.client.make_api_request.return_value = 204

    assert characterized_table.delete_row("1001") is True

    characterized_table.client.make_api_request.assert_called_once_with(
        "/api/database/rows/table/10/1001/", method="DELETE"
    )


def test_single_delete_rejects_an_unexpected_success_shape(characterized_table):
    characterized_table.client.make_api_request.return_value = {}

    with pytest.raises(RowDeleteError) as raised:
        characterized_table.delete_row(1001)

    assert isinstance(raised.value.__cause__, BaserowResponseError)


def test_table_move_validates_ids_and_returns_the_server_row(
    characterized_table, characterized_row_response
):
    moved_data = {**deepcopy(characterized_row_response), "order": "2.00000000000000000000"}
    characterized_table.client.make_api_request.return_value = moved_data

    moved = characterized_table.move_row("1001", before_id="1002")

    assert isinstance(moved, Row)
    assert moved.order == "2.00000000000000000000"
    characterized_table.client.make_api_request.assert_called_once_with(
        "/api/database/rows/table/10/1001/move/"
        "?user_field_names=true&before_id=1002",
        method="PATCH",
    )


@pytest.mark.parametrize("before_id", [0, True, "not-an-id"])
def test_table_move_rejects_invalid_before_ids_before_request(
    characterized_table, before_id
):
    with pytest.raises((TypeError, ValueError)):
        characterized_table.move_row(1001, before_id=before_id)

    characterized_table.client.make_api_request.assert_not_called()


def test_row_delete_delegates_to_table(characterized_row):
    characterized_row.table.delete_row = Mock(return_value=True)

    assert characterized_row.delete() is True

    characterized_row.table.delete_row.assert_called_once_with(characterized_row.id)


def test_row_move_delegates_synchronizes_and_returns_self(
    characterized_row, characterized_row_response
):
    moved = Row(
        row_data={**deepcopy(characterized_row_response), "order": "9.0"},
        table=characterized_row.table,
        client=characterized_row.client,
    )
    characterized_row.table.move_row = Mock(return_value=moved)

    returned = characterized_row.move(before_id=1002)

    assert returned is characterized_row
    assert characterized_row.order == "9.0"
    characterized_row.table.move_row.assert_called_once_with(
        characterized_row.id, before_id=1002
    )


def test_table_move_preserves_request_failure_as_cause(characterized_table):
    remote_error = RuntimeError("move failed")
    characterized_table.client.make_api_request.side_effect = remote_error

    with pytest.raises(RowMoveError) as raised:
        characterized_table.move_row(1001)

    assert raised.value.__cause__ is remote_error
