from typing import Optional, Any
from baserowapi.models.fields import PhoneNumberField
from baserowapi.models.row_values.row_value import RowValue
from baserowapi.exceptions import InvalidRowValueError


class PhoneNumberRowValue(RowValue):
    """
    Represents a RowValue specifically designed for a PhoneNumberField.

    Attributes:
        field (:class:`PhoneNumberField`): The associated PhoneNumberField object.
        raw_value (Optional[Any]): The raw value as fetched/returned from the API.
        client (Optional[Any]): The Baserow class API client. Some RowValue subclasses may require access to the API.
    """

    def __init__(
        self,
        field: "PhoneNumberField",
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize a PhoneNumberRowValue object.

        :param field: The associated PhoneNumberField object.
        :param raw_value: The raw value as fetched/returned from the API. Default is None.
        :param client: The Baserow class API client. Some RowValue subclasses may require access to the API. Default is None.
        :raises InvalidRowValueError: If the provided field is not an instance of the PhoneNumberField class.
        """
        super().__init__(field, raw_value, client)
        if not isinstance(field, PhoneNumberField):
            raise InvalidRowValueError(
                f"The provided field is not an instance of the PhoneNumberField class. Received: {type(field).__name__}"
            )
        self.logger.debug(
            f"Initialized PhoneNumberRowValue with field {self.field.name} and value {self._raw_value}"
        )

    @property
    def value(self) -> Any:
        """
        Get the value in a user-friendly format.

        :return: The raw value.
        """
        return self._raw_value

    @value.setter
    def value(self, new_value: Any) -> None:
        """
        Set a new phone number value.

        :param new_value: The new phone number value.
        :raises InvalidRowValueError: If the new value is not valid according to the field's validation rules.
        """
        try:
            self.field.validate_value(new_value)
            self._raw_value = new_value
            self.logger.debug(f"Set new value {new_value} for field {self.field.name}")
        except Exception as e:
            self.logger.error(
                f"Failed to set value for field {self.field.name}. Error: {e}"
            )
            raise InvalidRowValueError(
                f"Failed to set value for field {self.field.name}. Error: {e}"
            )
