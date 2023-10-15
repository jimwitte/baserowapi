import logging
import urllib.parse


class Filter:
    """
    Represents a filter expression used to filter results when fetching rows from a table.

    Attributes:
    - field_name (str): The name of the field to apply the filter on.
    - value (str, int, etc.): The value to compare against using the operator.
    - operator (str): The comparison operator. Default is "equal".

    Properties:
    - query_string (str): Computes the API's required GET parameter string.
    """

    def __init__(self, field_name: str, value: str, operator: str = "equal"):
        """
        Initializes the Filter object with the given field name, value, and operator.

        :param field_name: The name of the field.
        :param value: The value for comparison.
        :param operator: The comparison operator. Default is "equal".
        """

        self.logger = logging.getLogger(__name__)

        if not isinstance(field_name, str) or not field_name.strip():
            self.logger.error("field_name must be a non-empty string.")
            raise ValueError("field_name must be a non-empty string.")

        if not isinstance(operator, str) or not operator.strip():
            self.logger.error("operator must be a non-empty string.")
            raise ValueError("operator must be a non-empty string.")

        self.field_name = field_name
        self.value = value
        self.operator = operator

    @property
    def query_string(self) -> str:
        """
        Returns the filter as a query string formatted for use as a GET parameter in an API call.

        Format: filter__<encoded_field_name>__<operator>=<encoded_value>
        """
        # Encoding the field name and value for URL compatibility
        encoded_field_name = urllib.parse.quote_plus(self.field_name)
        encoded_value = urllib.parse.quote_plus(str(self.value))
        return f"filter__{encoded_field_name}__{self.operator}={encoded_value}"
