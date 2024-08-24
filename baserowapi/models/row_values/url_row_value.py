from typing import Optional, Any
from baserowapi.models.fields import UrlField
from baserowapi.models.row_values.row_value import RowValue
from baserowapi.exceptions import InvalidRowValueError


class UrlRowValue(RowValue):
    """
    Represents a RowValue specifically for a UrlField.

    Attributes:
        field (:class:`UrlField`): The associated UrlField object.
        raw_value (Optional[Any]): The raw value as returned/fetched from the API.
        client (Optional[Any]): The Baserow class API client. Some RowValue subclasses may need access to the API.
    """

    def __init__(
        self,
        field: "UrlField",
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize a UrlRowValue object.

        :param field: The associated UrlField object.
        :param raw_value: The raw value as returned/fetched from the API. Default is None.
        :param client: The Baserow class API client. Some RowValue subclasses may need access to the API. Default is None.
        :raises InvalidRowValueError: If the provided field is not an instance of the UrlField class.
        """
        super().__init__(field, raw_value, client)
        if not isinstance(field, UrlField):
            raise InvalidRowValueError(
                f"The provided field is not an instance of the UrlField class. Received: {type(field).__name__}"
            )
        self.logger.debug(
            f"Initialized UrlRowValue with field {self.field.name} and value {self._raw_value}"
        )
