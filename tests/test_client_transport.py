import logging
from io import BytesIO
from unittest.mock import Mock, patch

import pytest
import requests

from baserowapi import Baserow
from baserowapi.exceptions import BaserowTimeoutError


pytestmark = pytest.mark.offline


def response(status_code=200, body=b"{}", headers=None):
    result = requests.Response()
    result.status_code = status_code
    result._content = body
    result.raw = Mock()
    result.headers.update(headers or {"Content-Type": "application/json"})
    return result


@pytest.mark.parametrize("token", [None, "", "   ", 123])
def test_client_requires_a_non_empty_database_token(token):
    with pytest.raises(ValueError, match="token"):
        Baserow(token=token)


@pytest.mark.parametrize("timeout", [0, -1, True, "10"])
def test_client_rejects_invalid_timeout_defaults(timeout):
    with pytest.raises(ValueError, match="timeout"):
        Baserow(token="test-token", timeout=timeout)


@pytest.mark.parametrize("read_retries", [-1, True, 1.5])
def test_client_rejects_invalid_read_retry_counts(read_retries):
    with pytest.raises(ValueError, match="read_retries"):
        Baserow(token="test-token", read_retries=read_retries)


@pytest.mark.parametrize("batch_size", [True, 1.5, "10"])
def test_client_rejects_non_integer_default_batch_sizes(batch_size):
    with pytest.raises(TypeError, match="batch_size"):
        Baserow(token="test-token", batch_size=batch_size)


@pytest.mark.parametrize("batch_size", [0, -1])
def test_client_rejects_non_positive_default_batch_sizes(batch_size):
    with pytest.raises(ValueError, match="batch_size"):
        Baserow(token="test-token", batch_size=batch_size)


def test_constructing_client_does_not_configure_application_logging(monkeypatch):
    basic_config = Mock()
    monkeypatch.setattr(logging, "basicConfig", basic_config)

    Baserow(token="test-token")

    basic_config.assert_not_called()


def test_timeout_default_and_per_request_override_are_applied():
    client = Baserow(token="test-token", timeout=12)
    client._session.request = Mock(return_value=response())

    client.make_api_request("/default/")
    assert client._session.request.call_args.kwargs["timeout"] == 12

    client.make_api_request("/override/", timeout=3)
    assert client._session.request.call_args.kwargs["timeout"] == 3


def test_absolute_pagination_url_must_match_configured_origin():
    client = Baserow(token="test-token")
    client._session.request = Mock(return_value=response())

    client.make_api_request("https://api.baserow.io/next/")
    assert client._session.request.call_args.kwargs["url"] == (
        "https://api.baserow.io/next/"
    )

    with pytest.raises(ValueError, match="configured Baserow origin"):
        client.make_api_request("https://example.invalid/collect-token/")


@pytest.mark.parametrize("header_name", ["Authorization", "authorization"])
def test_authorization_header_cannot_be_overridden(header_name):
    client = Baserow(token="test-token")
    client._session.request = Mock(return_value=response())

    client.make_api_request(
        "/test/", headers={header_name: "Token replacement", "X-Test": "yes"}
    )

    sent_headers = client._session.request.call_args.kwargs["headers"]
    assert sent_headers["Authorization"] == "Token test-token"
    assert "authorization" not in sent_headers
    assert sent_headers["X-Test"] == "yes"


@pytest.mark.parametrize("header_name", ["Content-Type", "content-type"])
def test_file_upload_uses_client_session_without_json_content_type(header_name):
    client = Baserow(token="test-token")
    client._session.request = Mock(return_value=response())
    stream = BytesIO(b"example")

    client.make_api_request(
        "/upload/",
        method="POST",
        headers={header_name: "application/json"},
        files={"file": stream},
    )

    request = client._session.request.call_args.kwargs
    assert request["files"] == {"file": stream}
    assert "json" not in request
    assert "Content-Type" not in request["headers"]
    assert "content-type" not in request["headers"]
    assert "Content-Type" not in client._session.headers


def test_json_request_adds_json_content_type_without_mutating_session_headers():
    client = Baserow(token="test-token")
    client._session.request = Mock(return_value=response())

    client.make_api_request("/test/", method="POST", data={"value": 1})

    sent_headers = client._session.request.call_args.kwargs["headers"]
    assert sent_headers["Content-Type"] == "application/json"
    assert "Content-Type" not in client._session.headers


def test_safe_read_retries_transient_response_with_backoff():
    client = Baserow(token="test-token", read_retries=2)
    transient = response(503, b'{"error":"temporarily unavailable"}')
    client._session.request = Mock(side_effect=[transient, response()])

    with patch("baserowapi.baserow.time.sleep") as sleep:
        assert client.make_api_request("/test/") == {}

    assert client._session.request.call_count == 2
    sleep.assert_called_once_with(0.5)


def test_safe_read_respects_retry_after_header():
    client = Baserow(token="test-token", read_retries=1)
    limited = response(429, headers={"Retry-After": "2"})
    client._session.request = Mock(side_effect=[limited, response()])

    with patch("baserowapi.baserow.time.sleep") as sleep:
        client.make_api_request("/test/")

    sleep.assert_called_once_with(2.0)


@pytest.mark.parametrize("method", ["POST", "PATCH", "DELETE"])
def test_mutating_requests_are_never_retried(method):
    client = Baserow(token="test-token", read_retries=2)
    client._session.request = Mock(
        side_effect=requests.exceptions.Timeout("uncertain mutation")
    )

    with patch("baserowapi.baserow.time.sleep") as sleep:
        with pytest.raises(BaserowTimeoutError):
            client.make_api_request("/test/", method=method)

    client._session.request.assert_called_once()
    sleep.assert_not_called()


def test_request_support_methods_are_private():
    client = Baserow(token="test-token")

    assert not hasattr(client, "configure_logging")
    assert not hasattr(client, "get_combined_headers")
    assert not hasattr(client, "perform_request")
    assert not hasattr(client, "parse_response")
