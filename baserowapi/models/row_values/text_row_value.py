from typing import Optional, Any
from baserowapi.models.fields import TextField
from baserowapi.models.row_values.row_value import RowValue
from baserowapi.exceptions import InvalidRowValueError


class TextRowValue(RowValue):
    """
    Represents a RowValue specifically for a TextField.

    Attributes:
        field (:class:`TextField`): The associated TextField object.
        raw_value (Optional[Any]): The raw value as returned/fetched from the API.
        client (Optional[Any]): The Baserow class API client. Some RowValue subclasses may need access to the API.
    """

    def __init__(
        self,
        field: "TextField",
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize a TextRowValue object.

        :param field: The associated TextField object.
        :param raw_value: The raw value as returned/fetched from the API. Default is None.
        :param client: The Baserow class API client. Some RowValue subclasses may need access to the API. Default is None.
        :raises InvalidRowValueError: If the provided field is not an instance of the TextField class.
        """
        super().__init__(field, raw_value, client)
        if not isinstance(field, TextField):
            raise InvalidRowValueError(
                f"The provided field is not an instance of the TextField class. Received: {type(field).__name__}"
            )
        self.logger.debug(
            f"Initialized TextRowValue with field {self.field.name} and value {self._raw_value}"
        )
