import requests
import logging
from pathlib import Path
from typing import IO, Union, Dict, Optional, Any
from baserowapi.models.table import Table
from baserowapi.models.values import BaserowFile
import urllib.parse
from baserowapi.exceptions import (
    BaserowConnectionError,
    BaserowHTTPError,
    BaserowRequestError,
    BaserowResponseError,
    BaserowTimeoutError,
)


class Baserow:
    """
    A client class for interacting with the Baserow API.

    :ivar url: The base URL for the Baserow API.
    :vartype url: str
    :ivar token: The authentication token.
    :vartype token: str
    :ivar ERROR_MESSAGES: A dictionary mapping HTTP error codes to error messages.
    :vartype ERROR_MESSAGES: dict
    """

    ERROR_MESSAGES: Dict[int, str] = {
        400: "Bad request to {url}. The request contains invalid values or the JSON could not be parsed.",
        401: "Unauthorized request to {url}. Accessing an endpoint without a valid database token.",
        404: "Resource not found at {url}. Row or table is not found.",
        413: "Request entity too large at {url}. The request exceeded the maximum allowed payload size.",
        415: "Unsupported media type in request at {url}.",
        500: "Internal server error at {url}. The server encountered an unexpected condition.",
        502: "Bad gateway at {url}. Baserow is restarting or an unexpected outage is in progress.",
        503: "Service unavailable at {url}. The server could not process your request in time.",
    }

    def __init__(
        self,
        url: str = "https://api.baserow.io",
        token: Optional[str] = None,
        logging_level: int = logging.WARNING,
        log_file: Optional[str] = None,
        batch_size: int = 10,
    ) -> None:
        """
        Initialize a Baserow client.

        :param url: The base URL for the Baserow API. Defaults to 'https://api.baserow.io'.
        :type url: str
        :param token: The authentication token. Defaults to None.
        :type token: str, optional
        :param logging_level: The logging level. Defaults to logging.WARNING.
        :type logging_level: int
        :param log_file: The path to a log file. Defaults to None.
        :type log_file: str, optional
        :param batch_size: The default batch size for operations. Defaults to 10.
        :type batch_size: int
        """
        self.url = url
        self.token = token
        self.headers: Dict[str, str] = {
            "Authorization": f"Token {self.token}",
            "Content-Type": "application/json",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.configure_logging(logging_level, log_file)
        self.batch_size = batch_size

    def configure_logging(self, level: int, log_file: Optional[str]) -> None:
        """
        Configure logging for the Baserow client.

        :param level: The logging level.
        :type level: int
        :param log_file: The path to a log file. If provided, logs will also be written to this file.
        :type log_file: str, optional
        """
        handlers = [logging.StreamHandler()]
        if log_file:
            handlers.append(logging.FileHandler(log_file))

        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=handlers,
        )

    def __repr__(self) -> str:
        """
        Provide a string representation of the Baserow client.

        :return: A string representing the Baserow client with its base URL.
        :rtype: str
        """
        return f"Baserow client for base url {self.url}"

    def get_table(self, table_id: int) -> Table:
        """
        Retrieve a table instance based on its ID.

        :param table_id: The unique identifier of the table.
        :type table_id: int
        :return: An instance of the Table class.
        :rtype: Table
        """
        return Table(table_id, self)

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
        data: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10,
        files: Optional[Dict[str, IO[bytes]]] = None,
    ) -> Any:
        """
        Make an API request to the specified endpoint.

        :param endpoint: The API endpoint to make the request to.
        :type endpoint: str
        :param method: The HTTP method to use, by default "GET".
        :type method: str
        :param data: The data payload to send with the request, by default None.
        :type data: dict, optional
        :param headers: Additional headers to send with the request, by default None.
        :type headers: dict, optional
        :param timeout: The maximum number of seconds to wait for the server response, by default 10.
        :type timeout: int
        :param files: Files to be sent with the request, by default None.
        :type files: dict, optional
        :return: The parsed response data.
        :rtype: Any
        :raises BaserowHTTPError: If Baserow returns a non-successful HTTP response.
        :raises BaserowTimeoutError: If the request exceeds its timeout.
        :raises BaserowConnectionError: If a connection to Baserow cannot be established.
        :raises BaserowRequestError: If another request error prevents completion.
        :raises BaserowResponseError: If a JSON response cannot be decoded.
        """
        logger = logging.getLogger(__name__)

        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            parsed_base_url = urllib.parse.urlparse(self.url)
            parsed_endpoint_url = urllib.parse.urlparse(endpoint)
            url = parsed_endpoint_url._replace(scheme=parsed_base_url.scheme).geturl()
        else:
            url = self.url + endpoint

        combined_headers = self.get_combined_headers(headers)

        response = self.perform_request(
            method, url, combined_headers, data, timeout, files
        )

        if not 200 <= response.status_code < 300:
            error_code, description = self._get_error_details(response)
            fallback_message = self.ERROR_MESSAGES.get(
                response.status_code,
                "Baserow returned an unsuccessful response from {url}.",
            ).format(url=url)
            error_message = description or error_code or fallback_message
            logger.error(
                "Baserow request failed with HTTP %s: %s",
                response.status_code,
                error_message,
            )
            raise BaserowHTTPError(
                response.status_code,
                error_message,
                method=method,
                url=url,
                error_code=error_code,
                description=description,
            )

        return self.parse_response(response, method, url)

    def get_combined_headers(
        self, additional_headers: Optional[Dict[str, str]]
    ) -> Dict[str, str]:
        """
        Combines the default headers with any additional headers provided.

        :param additional_headers: Additional headers to combine with the default headers.
        :type additional_headers: dict, optional
        :return: Combined headers.
        :rtype: dict
        """
        return {**self.headers, **(additional_headers or {})}

    @staticmethod
    def _get_error_details(
        response: requests.Response,
    ) -> tuple[Optional[str], Optional[str]]:
        """Return Baserow's structured error code and description, when present."""
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

    def perform_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        data: Optional[Dict] = None,
        timeout: int = 10,
        files: Optional[Dict[str, Union[str, IO[bytes]]]] = None,
    ) -> requests.Response:
        """
        Performs an HTTP request using the given parameters.

        :param method: The HTTP method to use (e.g., "GET", "POST").
        :type method: str
        :param url: The complete URL to make the request to.
        :type url: str
        :param headers: Headers to send with the request.
        :type headers: dict
        :param data: The data payload to send with the request.
        :type data: dict, optional
        :param timeout: The maximum number of seconds to wait for the server response.
        :type timeout: int
        :param files: The files to send with the request, if any. The dictionary keys are
                      the form field names, and the values are the file data.
        :type files: dict, optional
        :return: The server's response to the request.
        :rtype: requests.Response
        :raises BaserowTimeoutError: If the request times out.
        :raises BaserowConnectionError: If a connection cannot be established.
        :raises BaserowRequestError: For other request execution failures.
        """
        logger = logging.getLogger(__name__)
        try:
            logger.debug(f"Making API request to: {url}")
            logger.debug(f"Request method: {method}")
            logger.debug(f"Request payload: {data}")

            if files:
                logger.debug(f"API file upload request: {files}")
                headers.pop("Content-Type", None)
                with requests.Session() as upload_session:
                    response = upload_session.request(
                        method=method,
                        url=url,
                        headers=headers,
                        files=files,
                        timeout=timeout,
                    )
            else:
                response = self.session.request(
                    method=method, url=url, headers=headers, json=data, timeout=timeout
                )

        except requests.exceptions.Timeout as e:
            logger.error(f"Request to {url} timed out.")
            raise BaserowTimeoutError(
                f"Request to {url} timed out.", method=method, url=url
            ) from e
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Could not connect to Baserow at {url}.")
            raise BaserowConnectionError(
                f"Could not connect to Baserow at {url}.", method=method, url=url
            ) from e
        except requests.exceptions.RequestException as e:
            logger.error(f"Request to {url} could not be completed: {e}")
            raise BaserowRequestError(
                f"Request to {url} could not be completed.", method=method, url=url
            ) from e

        return response

    def parse_response(
        self, response: requests.Response, method: str, url: str
    ) -> Union[int, Dict[str, Any], str, None]:
        """
        Parses the response received from an HTTP request.

        If the response has a status code of 204, it will return the status code.
        If the response body is empty and the method is not "DELETE" or the status code is not 204,
        a warning is logged.
        If the response body contains JSON, it attempts to parse and return the JSON.
        Otherwise, the raw response text is returned.

        :param response: The response object received from an HTTP request.
        :type response: requests.Response
        :param method: The HTTP method that was used for the request.
        :type method: str
        :param url: The complete URL the request was made to.
        :type url: str
        :return: Either the status code, a dictionary parsed from the JSON response, or the raw response text.
        :rtype: Union[int, dict, str, None]
        :raises BaserowResponseError: If a response advertised as JSON cannot be decoded.
        """
        logger = logging.getLogger(__name__)
        if response.status_code == 204:
            return response.status_code

        if not response.text:
            if method != "DELETE" or response.status_code != 204:
                logger.warning(f"No response body received from {url}")
            return None

        try:
            return response.json()
        except ValueError as e:
            content_type = response.headers.get("Content-Type", "").lower()
            if "json" in content_type:
                logger.error("Baserow returned an invalid JSON response from %s", url)
                raise BaserowResponseError(
                    f"Baserow returned an invalid JSON response from {url}.",
                    method=method,
                    url=url,
                ) from e
            return response.text
