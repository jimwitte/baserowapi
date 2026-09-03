"""Synchronous request client for Baserow's database-token API."""

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import logging
from pathlib import Path
import time
from typing import IO, Any, Mapping, Optional, Union
from urllib.parse import urlsplit

import requests
from requests.structures import CaseInsensitiveDict

from baserowapi.exceptions import (
    BaserowConnectionError,
    BaserowHTTPError,
    BaserowRequestError,
    BaserowResponseError,
    BaserowTimeoutError,
)
from baserowapi.models.table import Table
from baserowapi.models.values import BaserowFile


logger = logging.getLogger(__name__)


class Baserow:
    """Client for Baserow's database-token data API."""

    ERROR_MESSAGES: dict[int, str] = {
        400: "Bad request to {url}. The request contains invalid values or the JSON could not be parsed.",
        401: "Unauthorized request to {url}. Accessing an endpoint without a valid database token.",
        404: "Resource not found at {url}. Row or table is not found.",
        413: "Request entity too large at {url}. The request exceeded the maximum allowed payload size.",
        415: "Unsupported media type in request at {url}.",
        500: "Internal server error at {url}. The server encountered an unexpected condition.",
        502: "Bad gateway at {url}. Baserow is restarting or an unexpected outage is in progress.",
        503: "Service unavailable at {url}. The server could not process your request in time.",
    }
    _SAFE_RETRY_METHODS = frozenset({"GET", "HEAD"})
    _TRANSIENT_READ_STATUSES = frozenset({429, 502, 503, 504})
    _RETRY_BACKOFF_SECONDS = 0.5

    def __init__(
        self,
        url: str = "https://api.baserow.io",
        token: Optional[str] = None,
        batch_size: int = 10,
        timeout: float = 10,
        read_retries: int = 2,
    ) -> None:
        """Initialize a database-token client.

        ``timeout`` is the default for every request. ``read_retries`` applies
        only to GET and HEAD requests after transient connectivity, timeout,
        rate-limit, or service-availability failures. ``batch_size`` is the
        positive integer default used by plural row mutations.
        """
        if not isinstance(token, str) or not token.strip():
            raise ValueError("token must be a non-empty database token string.")
        if not isinstance(url, str) or not url.strip():
            raise ValueError("url must be a non-empty HTTP or HTTPS URL.")

        normalized_url = url.rstrip("/")
        parsed_url = urlsplit(normalized_url)
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.hostname:
            raise ValueError("url must be an absolute HTTP or HTTPS URL.")
        if parsed_url.query or parsed_url.fragment:
            raise ValueError("url must not contain a query string or fragment.")

        self._validate_timeout(timeout)
        if (
            isinstance(read_retries, bool)
            or not isinstance(read_retries, int)
            or read_retries < 0
        ):
            raise ValueError("read_retries must be a non-negative integer.")
        if isinstance(batch_size, bool) or not isinstance(batch_size, int):
            raise TypeError("batch_size must be a positive integer.")
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than zero.")

        self.url = normalized_url
        self.batch_size = batch_size
        self.timeout = timeout
        self.read_retries = read_retries
        self._origin = self._url_origin(parsed_url)
        self._authorization = f"Token {token}"
        self._session = requests.Session()
        self._session.headers.update({"Authorization": self._authorization})

    def __repr__(self) -> str:
        return f"Baserow client for base url {self.url}"

    def get_table(self, table_id: int) -> Table:
        """Return a new Table for a positive integer ID.

        The Table's field schema is loaded lazily.
        """
        return Table(table_id, self)

    def get_tables(self) -> list[Table]:
        """Return every table visible to this database token."""
        endpoint = "/api/database/tables/all-tables/"
        response = self.make_api_request(endpoint)
        if not isinstance(response, list):
            raise BaserowResponseError(
                "Baserow returned an invalid table-discovery response.",
                method="GET",
                url=endpoint,
            )

        tables: list[Table] = []
        for index, table_data in enumerate(response):
            if not isinstance(table_data, dict):
                raise BaserowResponseError(
                    f"Table-discovery item {index} is not an object.",
                    method="GET",
                    url=endpoint,
                )
            table_id = table_data.get("id")
            name = table_data.get("name")
            database_id = table_data.get("database_id")
            order = table_data.get("order")
            if (
                isinstance(table_id, bool)
                or not isinstance(table_id, int)
                or table_id <= 0
            ):
                raise BaserowResponseError(
                    f"Table-discovery item {index} has an invalid table ID.",
                    method="GET",
                    url=endpoint,
                )
            if not isinstance(name, str):
                raise BaserowResponseError(
                    f"Table-discovery item {index} has an invalid name.",
                    method="GET",
                    url=endpoint,
                )
            if isinstance(database_id, bool) or not isinstance(database_id, int):
                raise BaserowResponseError(
                    f"Table-discovery item {index} has an invalid database ID.",
                    method="GET",
                    url=endpoint,
                )
            if isinstance(order, bool) or not isinstance(order, (int, float)):
                raise BaserowResponseError(
                    f"Table-discovery item {index} has an invalid order.",
                    method="GET",
                    url=endpoint,
                )
            tables.append(Table(table_id, self, table_data=table_data))
        return tables

    @staticmethod
    def _uploaded_file_from_response(
        response: Any, *, endpoint: str
    ) -> BaserowFile:
        if not isinstance(response, dict) or not isinstance(response.get("name"), str):
            raise BaserowResponseError(
                "Baserow returned an invalid user-file object.", url=endpoint
            )
        return BaserowFile(
            name=response["name"],
            visible_name=response.get("visible_name"),
            url=response.get("url"),
            size=response.get("size"),
            mime_type=response.get("mime_type"),
            original_name=response.get("original_name"),
            raw=dict(response),
        )

    def upload_file(self, file_path: Union[str, Path]) -> BaserowFile:
        """Upload one local file and return it without assigning it to a row."""
        path = Path(file_path)
        endpoint = "/api/user-files/upload-file/"
        with path.open("rb") as stream:
            response = self.make_api_request(
                endpoint, method="POST", files={"file": stream}
            )
        return self._uploaded_file_from_response(response, endpoint=endpoint)

    def upload_file_via_url(self, url: str) -> BaserowFile:
        """Ask Baserow to import one URL and return the unattached user file."""
        if not isinstance(url, str) or not url:
            raise ValueError("A non-empty URL string is required.")
        endpoint = "/api/user-files/upload-via-url/"
        response = self.make_api_request(endpoint, method="POST", data={"url": url})
        return self._uploaded_file_from_response(response, endpoint=endpoint)

    def make_api_request(
        self,
        endpoint: str,
        method: str = "GET",
        data: Any = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[float] = None,
        files: Optional[Mapping[str, IO[bytes]]] = None,
    ) -> Any:
        """Make one authenticated request and return its parsed response.

        This is the low-level escape hatch for database-token endpoints not yet
        modeled by the package. It supplies authentication, timeout and safe
        read-retry behavior, package exceptions, and response parsing. It does
        not provide schema semantics or guarantee endpoint stability.
        """
        if not isinstance(method, str) or not method.strip():
            raise ValueError("method must be a non-empty string.")
        method = method.upper()
        request_timeout = self.timeout if timeout is None else timeout
        self._validate_timeout(request_timeout)
        url = self._build_url(endpoint)
        combined_headers = self._combined_headers(headers, has_files=files is not None)
        response = self._perform_request(
            method=method,
            url=url,
            headers=combined_headers,
            data=data,
            timeout=request_timeout,
            files=files,
        )

        if not 200 <= response.status_code < 300:
            error_code, description = self._get_error_details(response)
            diagnostic_url = self._safe_url_for_diagnostics(url)
            fallback_message = self.ERROR_MESSAGES.get(
                response.status_code,
                "Baserow returned an unsuccessful response from {url}.",
            ).format(url=diagnostic_url)
            logger.error(
                "Baserow %s request to %s failed with HTTP %s.",
                method,
                diagnostic_url,
                response.status_code,
            )
            raise BaserowHTTPError(
                response.status_code,
                fallback_message,
                method=method,
                url=diagnostic_url,
                error_code=error_code,
                description=description,
            )

        return self._parse_response(response, method, url)

    @staticmethod
    def _validate_timeout(timeout: float) -> None:
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
            raise ValueError("timeout must be a positive number of seconds.")
        if timeout <= 0:
            raise ValueError("timeout must be a positive number of seconds.")

    @staticmethod
    def _url_origin(parsed_url) -> tuple[str, str, int]:
        default_port = 443 if parsed_url.scheme == "https" else 80
        return (
            parsed_url.scheme.lower(),
            parsed_url.hostname.lower(),
            parsed_url.port or default_port,
        )

    @staticmethod
    def _safe_url_for_diagnostics(url: str) -> str:
        """Return a request URL without query values or fragments."""
        parsed_url = urlsplit(url)
        return parsed_url._replace(query="", fragment="").geturl()

    def _build_url(self, endpoint: str) -> str:
        if not isinstance(endpoint, str) or not endpoint:
            raise ValueError("endpoint must be a non-empty string.")
        parsed_endpoint = urlsplit(endpoint)
        if parsed_endpoint.scheme or parsed_endpoint.netloc:
            if parsed_endpoint.scheme not in {"http", "https"}:
                raise ValueError("endpoint must use HTTP or HTTPS.")
            if self._url_origin(parsed_endpoint) != self._origin:
                raise ValueError(
                    "Absolute endpoints must use the configured Baserow origin."
                )
            return endpoint
        if not endpoint.startswith("/"):
            raise ValueError("Relative endpoints must start with '/'.")
        return f"{self.url}{endpoint}"

    def _combined_headers(
        self,
        additional_headers: Optional[Mapping[str, str]],
        *,
        has_files: bool,
    ) -> dict[str, str]:
        if additional_headers is not None and not isinstance(
            additional_headers, Mapping
        ):
            raise TypeError("headers must be a mapping.")
        combined = CaseInsensitiveDict(self._session.headers)
        combined.update(additional_headers or {})
        combined["Authorization"] = self._authorization
        if has_files:
            combined.pop("Content-Type", None)
        else:
            combined.setdefault("Content-Type", "application/json")
        return dict(combined)

    @staticmethod
    def _get_error_details(
        response: requests.Response,
    ) -> tuple[Optional[str], Optional[str]]:
        try:
            error_data = response.json()
        except ValueError:
            return None, None
        if not isinstance(error_data, dict):
            return None, None
        error_code = error_data.get("error")
        description = error_data.get("description")
        return (
            str(error_code) if error_code is not None else None,
            str(description) if description is not None else None,
        )

    def _perform_request(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str],
        data: Any,
        timeout: float,
        files: Optional[Mapping[str, IO[bytes]]],
    ) -> requests.Response:
        is_safe_read = method in self._SAFE_RETRY_METHODS
        retry_limit = self.read_retries if is_safe_read else 0
        retry_number = 0
        diagnostic_url = self._safe_url_for_diagnostics(url)

        while True:
            logger.debug("Making Baserow %s request to %s", method, diagnostic_url)
            try:
                request_arguments: dict[str, Any] = {
                    "method": method,
                    "url": url,
                    "headers": headers,
                    "timeout": timeout,
                }
                if files is not None:
                    request_arguments["files"] = files
                    if data is not None:
                        request_arguments["data"] = data
                else:
                    request_arguments["json"] = data
                response = self._session.request(**request_arguments)
            except requests.exceptions.Timeout as error:
                if retry_number < retry_limit:
                    retry_number += 1
                    self._wait_before_retry(None, retry_number)
                    continue
                raise BaserowTimeoutError(
                    f"Request to {diagnostic_url} timed out.",
                    method=method,
                    url=diagnostic_url,
                ) from error
            except requests.exceptions.ConnectionError as error:
                if retry_number < retry_limit:
                    retry_number += 1
                    self._wait_before_retry(None, retry_number)
                    continue
                raise BaserowConnectionError(
                    f"Could not connect to Baserow at {diagnostic_url}.",
                    method=method,
                    url=diagnostic_url,
                ) from error
            except requests.exceptions.RequestException as error:
                raise BaserowRequestError(
                    f"Request to {diagnostic_url} could not be completed.",
                    method=method,
                    url=diagnostic_url,
                ) from error

            if (
                response.status_code in self._TRANSIENT_READ_STATUSES
                and retry_number < retry_limit
            ):
                retry_number += 1
                self._wait_before_retry(response, retry_number)
                continue
            return response

    def _wait_before_retry(
        self, response: Optional[requests.Response], retry_number: int
    ) -> None:
        delay = self._retry_delay(response, retry_number)
        if response is not None:
            response.close()
        logger.debug("Retrying safe Baserow read after %.3f seconds", delay)
        time.sleep(delay)

    def _retry_delay(
        self, response: Optional[requests.Response], retry_number: int
    ) -> float:
        retry_after = (
            response.headers.get("Retry-After") if response is not None else None
        )
        if retry_after:
            try:
                return max(0.0, float(retry_after))
            except ValueError:
                try:
                    retry_time = parsedate_to_datetime(retry_after)
                    if retry_time.tzinfo is None:
                        retry_time = retry_time.replace(tzinfo=timezone.utc)
                    return max(
                        0.0,
                        (retry_time - datetime.now(timezone.utc)).total_seconds(),
                    )
                except (TypeError, ValueError, OverflowError):
                    pass
        return self._RETRY_BACKOFF_SECONDS * (2 ** (retry_number - 1))

    @staticmethod
    def _parse_response(
        response: requests.Response, method: str, url: str
    ) -> Any:
        diagnostic_url = Baserow._safe_url_for_diagnostics(url)
        if response.status_code == 204:
            return response.status_code
        if not response.text:
            logger.warning("No response body received from %s", diagnostic_url)
            return None
        try:
            return response.json()
        except ValueError as error:
            content_type = response.headers.get("Content-Type", "").lower()
            if "json" in content_type:
                raise BaserowResponseError(
                    f"Baserow returned an invalid JSON response from {diagnostic_url}.",
                    method=method,
                    url=diagnostic_url,
                ) from error
            return response.text
