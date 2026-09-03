from unittest.mock import Mock

import pytest

from baserowapi import Baserow
from baserowapi.exceptions import BaserowResponseError, FieldDataRetrievalError


pytestmark = pytest.mark.offline


def discovered_table_data(table_id=10):
    return {
        "id": table_id,
        "name": "Example",
        "order": 1,
        "database_id": 20,
    }


def test_table_discovery_returns_tables_with_lossless_read_only_metadata():
    client = Baserow(token="test-token")
    client.make_api_request = Mock(return_value=[discovered_table_data()])

    tables = client.get_tables()

    assert len(tables) == 1
    assert tables[0].id == 10
    assert tables[0].name == "Example"
    assert tables[0].order == 1
    assert tables[0].database_id == 20
    assert dict(tables[0].metadata) == discovered_table_data()
    with pytest.raises(TypeError):
        tables[0].metadata["name"] = "Changed"


@pytest.mark.parametrize(
    "payload",
    [
        {},
        [None],
        [{"id": True, "name": "Bad", "order": 1, "database_id": 20}],
        [{"id": 10, "name": None, "order": 1, "database_id": 20}],
        [{"id": 10, "name": "Bad", "order": None, "database_id": 20}],
        [{"id": 10, "name": "Bad", "order": 1, "database_id": False}],
    ],
)
def test_table_discovery_rejects_malformed_responses(payload):
    client = Baserow(token="test-token")
    client.make_api_request = Mock(return_value=payload)

    with pytest.raises(BaserowResponseError):
        client.get_tables()


def test_get_table_instances_do_not_share_field_caches():
    client = Baserow(token="test-token")
    client.make_api_request = Mock(
        side_effect=[
            [{"id": 1, "name": "First", "type": "text", "order": 1}],
            [{"id": 2, "name": "Second", "type": "text", "order": 1}],
        ]
    )
    first_snapshot = client.get_table(10)
    second_snapshot = client.get_table(10)

    assert list(first_snapshot.fields) == ["First"]
    assert list(second_snapshot.fields) == ["Second"]
    assert first_snapshot.fields is not second_snapshot.fields
    assert client.make_api_request.call_count == 2


@pytest.mark.parametrize("table_id", [True, 1.5, "10"])
def test_get_table_rejects_non_integer_ids(table_id):
    client = Baserow(token="test-token")

    with pytest.raises(TypeError, match="table_id"):
        client.get_table(table_id)


@pytest.mark.parametrize("table_id", [0, -1])
def test_get_table_rejects_non_positive_ids(table_id):
    client = Baserow(token="test-token")

    with pytest.raises(ValueError, match="table_id"):
        client.get_table(table_id)


@pytest.mark.parametrize(
    "payload",
    [
        {},
        [None],
        [{"id": True, "name": "Name", "type": "text", "order": 0}],
        [{"id": 0, "name": "Name", "type": "text", "order": 0}],
        [{"name": "Name", "type": "text", "order": 0}],
        [{"id": 1, "name": "", "type": "text", "order": 0}],
        [{"id": 1, "name": "Name", "order": 0}],
        [{"id": 1, "name": "Name", "type": "", "order": 0}],
        [{"id": 1, "name": "Name", "type": "text"}],
        [{"id": 1, "name": "Name", "type": "text", "order": True}],
        [{"id": 1, "name": "Name", "type": "text", "order": -1}],
        [{"id": 1, "name": "Name", "type": "text", "order": float("nan")}],
    ],
)
def test_field_schema_rejects_malformed_successful_responses(payload):
    client = Baserow(token="test-token")
    client.make_api_request = Mock(return_value=payload)

    with pytest.raises(FieldDataRetrievalError) as raised:
        _ = client.get_table(10).fields

    assert isinstance(raised.value.__cause__, BaserowResponseError)


def test_field_schema_preserves_unknown_types_and_extra_metadata():
    field_data = {
        "id": 1,
        "name": "Future",
        "type": "future_type",
        "order": 0.5,
        "future_setting": {"preserve": True},
    }
    client = Baserow(token="test-token")
    client.make_api_request = Mock(return_value=[field_data])

    field = client.get_table(10).fields["Future"]

    assert field.type == "future_type"
    assert field.field_data == field_data
