import requests
import logging
from baserowapi.models.table import Table

class Baserow:
    def __init__(
            self, 
            url='https://api.baserow.io', 
            token=None, 
            logging_level=logging.WARNING, 
            log_file=None
        ):
        self.url = url
        self.token = token
        self.headers = {
            "Authorization": f"Token {self.token}",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.configure_logging(logging_level, log_file)

    def __repr__(self):
        return f"Baserow client for base url {self.url}"
    
    def configure_logging(self, level, log_file):
        handlers = [logging.StreamHandler()]
        if log_file:
            handlers.append(logging.FileHandler(log_file))
        
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=handlers
        )

    def get_table(self, table_id):
        """
        Retrieves a Table object given its ID.
        
        Args:
            table_id (int): The ID of the table to retrieve.
        
        Returns:
            Table: An initialized Table object.
        """
        return Table(table_id, self)


    ERROR_MESSAGES = {
        400: "Bad request to {url}. The request contains invalid values or the JSON could not be parsed.",
        401: "Unauthorized request to {url}. Accessing an endpoint without a valid database token.",
        404: "Resource not found at {url}. Row or table is not found.",
        413: "Request entity too large at {url}. The request exceeded the maximum allowed payload size.",
        500: "Internal server error at {url}. The server encountered an unexpected condition.",
        502: "Bad gateway at {url}. Baserow is restarting or an unexpected outage is in progress.",
        503: "Service unavailable at {url}. The server could not process your request in time.",
    }

    def make_api_request(self, endpoint, method="GET", data=None, headers=None, timeout=10):
        logger = logging.getLogger(__name__)

        url = self.url + endpoint
        combined_headers = self.get_combined_headers(headers)
        
        response = self.perform_request(method, url, combined_headers, data, timeout)
        
        if response.status_code in self.ERROR_MESSAGES:
            error_message = self.ERROR_MESSAGES[response.status_code].format(url=url)
            logger.error(error_message)
            raise Exception(error_message)
        
        return self.parse_response(response, method, url)

    def get_combined_headers(self, additional_headers):
        if additional_headers:
            return {**self.headers, **additional_headers}
        return self.headers

    def perform_request(self, method, url, headers, data, timeout):
        logger = logging.getLogger(__name__)
        try:
            logger.debug(f"api request: {url}")
            response = self.session.request(method, url, headers=headers, json=data, timeout=timeout)
            
            # Checking status code from ERROR_MESSAGES directly
            if response.status_code in self.ERROR_MESSAGES:
                error_message = self.ERROR_MESSAGES[response.status_code].format(url=url)
                logger.error(error_message)
                raise requests.exceptions.HTTPError(error_message, response=response)
            return response
        except requests.exceptions.Timeout:
            logger.error(f"Request to {url} timed out.")
            raise
        except requests.exceptions.RequestException as e:
            # Handle any other exceptions here
            error_message = f"Unexpected error occurred while making a request to {url}: {e}"
            logger.error(error_message)
            raise Exception(error_message)

    def parse_response(self, response, method, url):
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
