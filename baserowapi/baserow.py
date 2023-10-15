import requests
import logging
from typing import IO, Union, Dict, Optional, Any
from baserowapi.models.table import Table


class Baserow:
    """
    A client class for interacting with the Baserow API.

    :ivar url: The base URL for the Baserow API.
    :ivar token: The authentication token.
    :ivar ERROR_MESSAGES: A dictionary mapping HTTP error codes to error messages.
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
    ) -> None:
        """
        Initialize a Baserow client.

        :param url: The base URL for the Baserow API. Defaults to 'https://api.baserow.io'.
        :param token: The authentication token. Defaults to None.
        :param logging_level: The logging level. Defaults to logging.WARNING.
        :param log_file: The path to a log file. Defaults to None.
        :ivar headers: Headers for the API request.
        :ivar session: A session object for making API requests.
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

    def configure_logging(self, level: int, log_file: Optional[str]) -> None:
        """
        Configure logging for the Baserow client.

        :param level: The logging level.
        :param log_file: The path to a log file. If provided, logs will also be written to this file.
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
        """
        return f"Baserow client for base url {self.url}"

    def get_table(self, table_id: int) -> Table:
        """
        Retrieve a table instance based on its ID.

        :param table_id: The unique identifier of the table.
        :return: An instance of the Table class.
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
        :param method: The HTTP method to use, by default "GET".
        :param data: The data payload to send with the request, by default None.
        :param headers: Additional headers to send with the request, by default None.
        :param timeout: The maximum number of seconds to wait for the server response, by default 10.
        :param files: Files to be sent with the request, by default None.
        :return: The parsed response data.
        """
        logger = logging.getLogger(__name__)

        url = self.url + endpoint
        combined_headers = self.get_combined_headers(headers)

        response = self.perform_request(
            method, url, combined_headers, data, timeout, files
        )

        if response.status_code in self.ERROR_MESSAGES:
            error_message = self.ERROR_MESSAGES[response.status_code].format(url=url)
            logger.error(error_message)
            raise Exception(error_message)

        return self.parse_response(response, method, url)

    def get_combined_headers(
        self, additional_headers: Optional[Dict[str, str]]
    ) -> Dict[str, str]:
        """
        Combines the default headers with any additional headers provided.

        :param additional_headers: Additional headers to combine with the default headers.
        :return: Combined headers.
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
        :param url: The complete URL to make the request to.
        :param headers: Headers to send with the request.
        :param data: The data payload to send with the request.
        :param timeout: The maximum number of seconds to wait for the server response.
        :param files: The files to send with the request, if any. The dictionary keys are
                    the form field names, and the values are the file data.
        :return: The server's response to the request.
        :raises requests.exceptions.HTTPError: If the response status code is in the defined ERROR_MESSAGES.
        :raises requests.exceptions.Timeout: If the request times out.
        :raises requests.exceptions.RequestException: For other request-related exceptions like connectivity issues.
        :raises Exception: For any other unexpected exceptions.
        """
        logger = logging.getLogger(__name__)
        try:
            logger.debug(f"Making API request: {url}")

            # Conditionally adjust headers for file uploads
            if files:
                logger.debug(f"API file upload request {files}")
                headers.pop("Content-Type", None)
                # session.request seems to insist on header "Content: application/json" :-(
                response = requests.post(url=url, headers=headers, files=files)
            else:
                response = self.session.request(
                    method=method, url=url, headers=headers, json=data, timeout=timeout
                )

            # Checking status code from ERROR_MESSAGES directly
            if response.status_code in self.ERROR_MESSAGES:
                error_message = self.ERROR_MESSAGES[response.status_code].format(
                    url=url
                )
                logger.error(error_message)
                raise requests.exceptions.HTTPError(error_message, response=response)
            return response
        except requests.exceptions.Timeout:
            logger.error(f"Request to {url} timed out.")
            raise
        except requests.exceptions.RequestException as e:
            # Handle any other exceptions here
            error_message = (
                f"Unexpected error occurred while making a request to {url}: {e}"
            )
            logger.debug(f"JSON payload: {data}")
            logger.error(error_message)
            raise Exception(error_message)

    def parse_response(
        self, response: requests.Response, method: str, url: str
    ) -> Union[int, Dict[str, Any], str]:
        """
        Parses the response received from an HTTP request.

        If the response has a status code of 204, it will return the status code.
        If the response body is empty and the method is not "DELETE" or the status code is not 204,
        a warning is logged.
        If the response body contains JSON, it attempts to parse and return the JSON.
        Otherwise, the raw response text is returned.

        :param response: The response object received from an HTTP request.
        :param method: The HTTP method that was used for the request.
        :param url: The complete URL the request was made to.
        :return: Either the status code, a dictionary parsed from the JSON response, or the raw response text.
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
