from typing import Optional, Any
from baserowapi.models.fields import DateField
from baserowapi.models.row_values.base_date_row_value import BaseDateRowValue
from baserowapi.exceptions import InvalidRowValueError


class DateRowValue(BaseDateRowValue):
    """
    Represents a RowValue specifically designed for a DateField.

    Attributes:
        field (:class:`DateField`): The associated DateField object.
        raw_value (Optional[str]): The raw date value as fetched/returned from the API, typically in ISO format.
        client (Optional[Any]): The Baserow class API client. Some RowValue subclasses may require access to the API.
    """

    def __init__(
        self,
        field: "DateField",
        raw_value: Optional[str] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize a DateRowValue object.

        :param field: The associated DateField object.
        :param raw_value: The raw date value as fetched/returned from the API, typically in ISO format. Default is None.
        :param client: The Baserow class API client. Some RowValue subclasses may require access to the API. Default is None.
        :raises InvalidRowValueError: If the provided field is not an instance of DateField.
        """
        super().__init__(field, raw_value, client)
        if not isinstance(field, DateField):
            raise InvalidRowValueError(
                f"The provided field is not an instance of the DateField class. Received: {type(field).__name__}"
            )
