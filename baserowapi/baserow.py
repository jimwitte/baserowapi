import requests
import logging
from typing import IO, Union, Dict, Optional, Any
from baserowapi.models.table import Table
import urllib.parse
from baserowapi.exceptions import BaserowHTTPError


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
        :raises BaserowHTTPError: If the response status code is in the defined ERROR_MESSAGES.
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

        if response.status_code in self.ERROR_MESSAGES:
            error_message = self.ERROR_MESSAGES[response.status_code].format(url=url)
            logger.error(error_message)
            raise BaserowHTTPError(response.status_code, error_message)

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
        if additional_headers:
            return {**self.headers, **additional_headers}
        return self.headers

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
        :raises requests.exceptions.HTTPError: If the response status code is in the defined ERROR_MESSAGES.
        :raises requests.exceptions.Timeout: If the request times out.
        :raises requests.exceptions.RequestException: For other request-related exceptions like connectivity issues.
        :raises Exception: For any other unexpected exceptions.
        """
        logger = logging.getLogger(__name__)
        try:
            logger.debug(f"Making API request to: {url}")
            logger.debug(f"Request method: {method}")
            logger.debug(f"Request payload: {data}")

            if files:
                upload_session = requests.Session()
                logger.debug(f"API file upload request: {files}")
                headers.pop("Content-Type", None)
                logger.debug(f"Files being uploaded: {files}")
                logger.debug(f"Headers being sent: {headers}")
                response = upload_session.request(
                    method="POST",
                    url=url,
                    headers=headers,
                    files=files,
                    timeout=timeout,
                )
            else:
                response = self.session.request(
                    method=method, url=url, headers=headers, json=data, timeout=timeout
                )

            response.raise_for_status()

        except requests.exceptions.Timeout:
            logger.error(f"Request to {url} timed out.")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Unexpected error occurred while making a request to {url}: {e}"
            )
            logger.debug(f"Request payload: {data}")
            raise Exception(
                f"Unexpected error occurred while making a request to {url}: {e}"
            )

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
        :raises ValueError: If the response cannot be parsed as JSON.
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
        except ValueError:
            logger.error(f"Failed to parse response as JSON. Received: {response.text}")
            return response.text
