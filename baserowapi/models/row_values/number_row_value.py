from typing import Optional, Union, List, Any
from baserowapi.models.fields import NumberField
from baserowapi.models.row_values.row_value import RowValue
from baserowapi.exceptions import InvalidRowValueError, RowValueOperationError


class NumberRowValue(RowValue):
    """
    Represents a RowValue specifically designed for a NumberField.

    Attributes:
        field (:class:`NumberField`): The associated NumberField object.
        raw_value (Optional[str]): The raw numeric value as fetched/returned from the API.
        client (Optional[Any]): The Baserow class API client. Some RowValue subclasses may require access to the API.
    """

    def __init__(
        self,
        field: "NumberField",
        raw_value: Optional[str] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize a NumberRowValue object.

        :param field: The associated NumberField object.
        :param raw_value: The raw numeric value as fetched/returned from the API. Default is None.
        :param client: The Baserow class API client. Some RowValue subclasses may require access to the API. Default is None.
        :raises InvalidRowValueError: If the provided field is not an instance of the NumberField class.
        """
        super().__init__(field, raw_value, client)
        if not isinstance(field, NumberField):
            raise InvalidRowValueError(
                f"The provided field is not an instance of the NumberField class. Received: {type(field).__name__}"
            )
        self.logger.debug(
            f"Initialized NumberRowValue with field {self.field.name} and value {self._raw_value}"
        )

    @property
    def value(self) -> str:
        """
        Get the value in a user-friendly format.
        For NumberRowValue, this returns the raw value as a string.

        :return: The raw value as a string.
        """
        return self._raw_value

    @value.setter
    def value(self, new_value: str) -> None:
        """
        Set a new value.
        This should handle validation specific to NumberRowValue using the associated NumberField's validate_value method.

        :param new_value: The new numeric value to set as a string.
        :raises RowValueOperationError: If the value is not valid as per the associated NumberField's validation.
        """
        try:
            numeric_value = float(new_value)
            self.field.validate_value(numeric_value)
            self._raw_value = new_value
            self.logger.debug(f"Set new value {new_value} for field {self.field.name}")
        except Exception as e:
            self.logger.error(
                f"Failed to set value for field {self.field.name}. Error: {e}"
            )
            raise RowValueOperationError(
                f"Failed to set value for field {self.field.name}. Error: {e}"
            )
