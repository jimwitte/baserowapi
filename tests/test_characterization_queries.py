import json
from collections.abc import Iterator
from urllib.parse import parse_qs, urlsplit

import pytest

from baserowapi import Filter
from baserowapi.exceptions import BaserowResponseError, RowFetchError


pytestmark = pytest.mark.offline


def test_current_filter_tree_serialization(characterized_table):
    url = characterized_table._build_request_url(
        include=["Name", "Status"],
        order_by=["-Name"],
        filter_type="AND",
        filters=[
            Filter("Name", "Example", "equal"),
            Filter("Status", 101, "single_select_equal"),
        ],
        size=50,
    )

    query = parse_qs(urlsplit(url).query)
    assert query["user_field_names"] == ["true"]
    assert query["include"] == ["Name,Status"]
    assert query["order_by"] == ["-Name"]
    assert query["size"] == ["50"]
    assert json.loads(query["filters"][0]) == {
        "filter_type": "AND",
        "filters": [
            {"field": "Name", "type": "equal", "value": "Example"},
            {"field": "Status", "type": "single_select_equal", "value": 101},
        ],
        "groups": [],
    }


def test_get_rows_and_iter_rows_have_fixed_return_types(characterized_table):
    characterized_table.client.make_api_request.return_value = {
        "results": [],
        "next": None,
    }

    iterator = characterized_table.iter_rows()

    assert isinstance(iterator, Iterator)
    assert iter(iterator) is iterator
    assert list(iterator) == []
    assert characterized_table.get_rows() == []


def test_zero_limit_returns_no_rows_without_a_request(characterized_table):
    assert list(characterized_table.iter_rows(limit=0)) == []
    assert characterized_table.get_rows(limit=0) == []

    characterized_table.client.make_api_request.assert_not_called()


@pytest.mark.parametrize("parameter", ["view_id", "size"])
@pytest.mark.parametrize("value", [0, -1])
def test_positive_query_parameters_reject_zero_and_negative_values(
    characterized_table, parameter, value
):
    with pytest.raises(ValueError, match=parameter):
        characterized_table.get_rows(**{parameter: value})

    characterized_table.client.make_api_request.assert_not_called()


@pytest.mark.parametrize("parameter", ["view_id", "size", "limit"])
@pytest.mark.parametrize("value", [True, 1.5, "2"])
def test_numeric_query_parameters_reject_non_integer_values(
    characterized_table, parameter, value
):
    with pytest.raises(TypeError, match=parameter):
        characterized_table.get_rows(**{parameter: value})

    characterized_table.client.make_api_request.assert_not_called()


def test_negative_limit_is_rejected(characterized_table):
    with pytest.raises(ValueError, match="limit"):
        characterized_table.get_rows(limit=-1)

    characterized_table.client.make_api_request.assert_not_called()


@pytest.mark.parametrize(
    "response",
    [
        None,
        {},
        {"results": None, "next": None},
        {"results": [], "next": 2},
        {"results": [{"Name": "missing ID"}], "next": None},
        {"results": [{"id": True}], "next": None},
    ],
)
def test_malformed_row_pages_raise_instead_of_appearing_empty(
    characterized_table, response
):
    characterized_table.client.make_api_request.return_value = response

    with pytest.raises(RowFetchError) as raised:
        characterized_table.get_rows()

    assert isinstance(raised.value.__cause__, BaserowResponseError)


def test_current_pagination_follows_server_next_url(characterized_table):
    characterized_table.client.make_api_request.side_effect = [
        {
            "results": [{"id": 1, "order": "1.0", "Name": "First"}],
            "next": "https://api.baserow.io/api/database/rows/table/10/?page=2",
        },
        {
            "results": [{"id": 2, "order": "2.0", "Name": "Second"}],
            "next": None,
        },
    ]

    rows = characterized_table.get_rows()

    assert [row.id for row in rows] == [1, 2]
    assert characterized_table.client.make_api_request.call_args_list[1].args == (
        "https://api.baserow.io/api/database/rows/table/10/?page=2",
    )


def test_singular_create_returns_row_and_uses_field_encoding(
    characterized_table, characterized_row_response
):
    characterized_table.client.make_api_request.return_value = characterized_row_response
    submitted = {
        "Name": "Created",
        "Tags": characterized_table.fields["Tags"].options,
    }

    created = characterized_table.add_row(submitted)

    assert created.id == characterized_row_response["id"]
    assert characterized_table.client.make_api_request.call_args.kwargs["data"] == {
        "Name": "Created",
        "Tags": [option.id for option in characterized_table.fields["Tags"].options],
    }


def test_batch_mapping_update_uses_field_encoding(
    characterized_table, characterized_row_response
):
    characterized_table.client.make_api_request.return_value = {
        "items": [characterized_row_response]
    }
    submitted = {"id": 1001, "Date Time": "2026-09-01T00:00:00+00:00"}

    characterized_table.update_rows([submitted])

    assert characterized_table.client.make_api_request.call_args.kwargs["data"] == {
        "items": [{"id": 1001, "Date Time": "2026-09-01T00:00:00Z"}]
    }


def test_single_row_update_encodes_an_explicit_iso_datetime(
    characterized_row, characterized_row_response
):
    characterized_row.client.make_api_request.return_value = characterized_row_response

    characterized_row.update({"Date Time": "2026-09-01T00:00:00+00:00"})

    assert characterized_row.client.make_api_request.call_args.kwargs["data"] == {
        "Date Time": "2026-09-01T00:00:00Z"
    }
