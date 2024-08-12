from typing import Optional, Any
from baserowapi.models.fields import EmailField
from baserowapi.models.row_values.row_value import RowValue
from baserowapi.exceptions import InvalidRowValueError


class EmailRowValue(RowValue):
    """
    Represents a RowValue specifically designed for an EmailField.

    Attributes:
        field (:class:`EmailField`): The associated EmailField object.
        raw_value (Optional[Any]): The raw value as fetched/returned from the API.
        client (Optional[Any]): The Baserow class API client. Some RowValue subclasses may require access to the API.
    """

    def __init__(
        self,
        field: "EmailField",
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize an EmailRowValue object.

        :param field: The associated EmailField object.
        :param raw_value: The raw value as fetched/returned from the API. Default is None.
        :param client: The Baserow class API client. Some RowValue subclasses may require access to the API. Default is None.
        :raises InvalidRowValueError: If the provided field is not an instance of EmailField.
        """
        super().__init__(field, raw_value, client)
        if not isinstance(field, EmailField):
            raise InvalidRowValueError(
                f"The provided field is not an instance of the EmailField class. Received: {type(field).__name__}"
            )
        self.logger.debug(
            f"Initialized EmailRowValue with field {self.field.name} and value {self._raw_value}"
        )
