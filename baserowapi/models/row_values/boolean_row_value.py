from typing import Optional, Any
from baserowapi.models.fields import BooleanField
from baserowapi.models.row_values.row_value import RowValue
from baserowapi.exceptions import InvalidRowValueError


class BooleanRowValue(RowValue):
    """
    Represents a RowValue specifically designed for a BooleanField.

    Attributes:
        field (:class:`BooleanField`): The associated BooleanField object.
        raw_value (Optional[bool]): The raw boolean value as fetched/returned from the API.
        client (Optional[Any]): The Baserow class API client. Some RowValue subclasses may require access to the API.
    """

    def __init__(
        self,
        field: "BooleanField",
        raw_value: Optional[bool] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize a BooleanRowValue object.

        :param field: The associated BooleanField object.
        :param raw_value: The raw boolean value as fetched/returned from the API. Default is None.
        :param client: The Baserow class API client. Some RowValue subclasses may require access to the API. Default is None.
        :raises InvalidRowValueError: If the provided field is not an instance of BooleanField.
        """
        super().__init__(field, raw_value, client)
        if not isinstance(field, BooleanField):
            raise InvalidRowValueError(
                f"The provided field is not an instance of the BooleanField class. Received: {type(field).__name__}"
            )
        self.logger.debug(
            f"Initialized BooleanRowValue with field {self.field.name} and value {self._raw_value}"
        )

    @property
    def value(self) -> Optional[bool]:
        """
        Get the value in a user-friendly format.
        For BooleanRowValue, this returns the raw value as a boolean or None.

        :return: The boolean value of the raw_value or None.
        """
        return self._raw_value

    @value.setter
    def value(self, new_value: Optional[bool]) -> None:
        """
        Set a new value.
        This should handle validation specific to BooleanRowValue using the associated BooleanField's validate_value method.

        :param new_value: The new boolean value to set.
        :raises InvalidRowValueError: If the value is not valid as per the associated BooleanField's validation.
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
