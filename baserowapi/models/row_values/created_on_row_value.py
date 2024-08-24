from typing import Optional, Any
from baserowapi.models.fields import CreatedOnField
from baserowapi.models.row_values.base_date_row_value import BaseDateRowValue
from baserowapi.exceptions import InvalidRowValueError, ReadOnlyValueError


class CreatedOnRowValue(BaseDateRowValue):
    """
    Represents a RowValue specifically designed for a CreatedOnField.

    Attributes:
        field (:class:`CreatedOnField`): The associated CreatedOnField object.
        raw_value (Optional[str]): The raw date value as fetched/returned from the API, typically in ISO format.
        client (Optional[Any]): The Baserow class API client. Some RowValue subclasses may require access to the API.
    """

    def __init__(
        self,
        field: "CreatedOnField",
        raw_value: Optional[str] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize a CreatedOnRowValue object.

        :param field: The associated CreatedOnField object.
        :param raw_value: The raw date value as fetched/returned from the API, typically in ISO format. Default is None.
        :param client: The Baserow class API client. Some RowValue subclasses may require access to the API. Default is None.
        :raises InvalidRowValueError: If the provided field is not an instance of CreatedOnField.
        """
        super().__init__(field, raw_value, client)
        if not isinstance(field, CreatedOnField):
            raise InvalidRowValueError(
                f"The provided field is not an instance of the CreatedOnField class. Received: {type(field).__name__}"
            )

    @BaseDateRowValue.value.setter
    def value(self, new_value: str) -> None:
        """
        Set a new value for CreatedOnRowValue.
        As CreatedOnRowValue is read-only, it will raise an error if there's an attempt to set a value.

        :param new_value: The new value to be set.
        :raises ReadOnlyValueError: If there's an attempt to set a value for a read-only field.
        """
        msg = "Cannot set value for a read-only CreatedOnRowValue."
        self.logger.error(msg)
        raise ReadOnlyValueError(msg)
