from unittest.mock import Mock

import pytest
import requests

from baserowapi import Baserow
from baserowapi.exceptions import (
    BaserowConnectionError,
    BaserowHTTPError,
    BaserowRequestError,
    BaserowResponseError,
    BaserowTimeoutError,
    FieldValidationError,
    RowFetchError,
)
from baserowapi.models.row import Row

pytestmark = pytest.mark.offline


def make_response(
    status_code=200, body=b"{}", content_type="application/json"
):
    response = requests.Response()
    response.status_code = status_code
    response._content = body
    response.headers["Content-Type"] = content_type
    response.url = "https://api.baserow.io/test/"
    return response


@pytest.mark.parametrize("status_code", [302, 400, 401, 403, 404, 429, 500])
def test_every_http_error_status_raises_baserow_http_error(status_code):
    client = Baserow(token="test-token")
    response = make_response(
        status_code,
        b'{"error":"ERROR_TEST","description":"Test failure"}',
    )
    client.session.request = Mock(return_value=response)

    with pytest.raises(BaserowHTTPError) as raised:
        client.make_api_request("/test/")

    assert raised.value.status_code == status_code
    assert raised.value.error_code == "ERROR_TEST"
    assert raised.value.description == "Test failure"
    assert raised.value.method == "GET"


def test_timeout_is_translated_and_chained():
    client = Baserow(token="test-token")
    original_error = requests.exceptions.Timeout("too slow")
    client.session.request = Mock(side_effect=original_error)

    with pytest.raises(BaserowTimeoutError) as raised:
        client.make_api_request("/test/")

    assert raised.value.__cause__ is original_error


def test_connection_error_is_translated_and_chained():
    client = Baserow(token="test-token")
    original_error = requests.exceptions.ConnectionError("unavailable")
    client.session.request = Mock(side_effect=original_error)

    with pytest.raises(BaserowConnectionError) as raised:
        client.make_api_request("/test/")

    assert raised.value.__cause__ is original_error


def test_other_request_error_is_translated_and_chained():
    client = Baserow(token="test-token")
    original_error = requests.exceptions.RequestException("request failed")
    client.session.request = Mock(side_effect=original_error)

    with pytest.raises(BaserowRequestError) as raised:
        client.make_api_request("/test/")

    assert raised.value.__cause__ is original_error


def test_invalid_advertised_json_raises_response_error():
    client = Baserow(token="test-token")
    client.session.request = Mock(return_value=make_response(body=b"not-json"))

    with pytest.raises(BaserowResponseError):
        client.make_api_request("/test/")


def test_plain_text_response_remains_supported():
    client = Baserow(token="test-token")
    client.session.request = Mock(
        return_value=make_response(body=b"plain text", content_type="text/plain")
    )

    assert client.make_api_request("/test/") == "plain text"


def test_no_content_response_returns_status_code():
    client = Baserow(token="test-token")
    client.session.request = Mock(return_value=make_response(204, b""))

    assert client.make_api_request("/test/", method="DELETE") == 204


def test_request_headers_are_copied_before_per_request_changes():
    client = Baserow(token="test-token")

    combined_headers = client.get_combined_headers(None)
    combined_headers.pop("Content-Type")

    assert client.headers["Content-Type"] == "application/json"


def test_high_level_row_fetch_preserves_domain_error_and_http_cause():
    client = Mock()
    http_error = BaserowHTTPError(404, "Row not found")
    client.make_api_request.side_effect = http_error
    table = Baserow(token="test-token").get_table(1)
    table.client = client

    with pytest.raises(RowFetchError) as raised:
        table.get_row(999999)

    assert raised.value.__cause__ is http_error


def test_row_update_does_not_convert_field_validation_error():
    validation_error = FieldValidationError("invalid value")
    field = Mock()
    field.validate_value.side_effect = validation_error
    table = Mock()
    table.id = 1
    table.writable_fields = ["Name"]
    table.fields = {"Name": field}
    row = Row(
        row_data={"id": 1, "order": 1, "Name": "original"},
        table=table,
        client=Mock(),
    )

    with pytest.raises(FieldValidationError) as raised:
        row.update({"Name": "invalid"})

    assert raised.value is validation_error
