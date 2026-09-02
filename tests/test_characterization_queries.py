import json
from types import GeneratorType
from urllib.parse import parse_qs, urlsplit

import pytest

from baserowapi import Filter


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


def test_get_rows_iterator_switches_return_type(characterized_table):
    characterized_table.client.make_api_request.return_value = {
        "results": [],
        "next": None,
    }

    iterator = characterized_table.get_rows(iterator=True)

    assert isinstance(iterator, GeneratorType)
    assert list(iterator) == []
    assert characterized_table.get_rows(iterator=False) == []


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


def test_current_create_returns_list_and_bypasses_field_encoding(
    characterized_table, characterized_row_response
):
    characterized_table.client.make_api_request.return_value = {
        "items": [characterized_row_response]
    }
    submitted = {"Name": "Created", "Tags": "Urgent,Customer"}

    created = characterized_table.add_rows(submitted)

    assert isinstance(created, list)
    assert len(created) == 1
    assert characterized_table.client.make_api_request.call_args.kwargs["data"] == {
        "items": [submitted]
    }


def test_current_batch_mapping_update_validates_but_does_not_encode(
    characterized_table, characterized_row_response
):
    characterized_table.client.make_api_request.return_value = {
        "items": [characterized_row_response]
    }
    submitted = {"id": 1001, "Date Time": "2026-09-01T00:00:00+00:00"}

    characterized_table.update_rows([submitted])

    assert characterized_table.client.make_api_request.call_args.kwargs["data"] == {
        "items": [submitted]
    }


def test_single_row_update_encodes_an_explicit_iso_datetime(
    characterized_row, characterized_row_response
):
    characterized_row.client.make_api_request.return_value = characterized_row_response

    characterized_row.update({"Date Time": "2026-09-01T00:00:00+00:00"})

    assert characterized_row.client.make_api_request.call_args.kwargs["data"] == {
        "Date Time": "2026-09-01T00:00:00Z"
    }
