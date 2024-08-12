from typing import Optional, Any
from baserowapi.models.row_values.row_value import RowValue
from baserowapi.models.fields import LongTextField
from baserowapi.exceptions import InvalidRowValueError


class LongTextRowValue(RowValue):
    """
    Represents a RowValue specifically for a LongTextField.

    Attributes:
        field (:class:`LongTextField`): The associated LongTextField object.
        raw_value (Optional[Any]): The raw value as returned/fetched from the API.
        client (Optional[Any]): The Baserow class API client. Some RowValue subclasses may need access to the API.
    """

    def __init__(
        self,
        field: "LongTextField",
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize a LongTextRowValue object.

        :param field: The associated LongTextField object.
        :param raw_value: The raw value as returned/fetched from the API. Default is None.
        :param client: The Baserow class API client. Some RowValue subclasses may need access to the API. Default is None.
        :raises InvalidRowValueError: If the provided field is not an instance of the LongTextField class.
        """
        super().__init__(field, raw_value, client)
        if not isinstance(field, LongTextField):
            raise InvalidRowValueError(
                f"The provided field is not an instance of the LongTextField class. Received: {type(field).__name__}"
            )
        self.logger.debug(
            f"Initialized LongTextRowValue with field {self.field.name} and value {self._raw_value}"
        )
