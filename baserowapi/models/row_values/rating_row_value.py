from typing import Optional, Union, Any
from baserowapi.models.fields import RatingField
from baserowapi.models.row_values.row_value import RowValue
from baserowapi.exceptions import InvalidRowValueError


class RatingRowValue(RowValue):
    """
    Represents a RowValue specifically designed for a RatingField.

    Attributes:
        field (:class:`RatingField`): The associated RatingField object.
        raw_value (Optional[Union[int, float]]): The raw numerical value as fetched/returned from the API.
        client (Optional[Any]): The Baserow class API client. Some RowValue subclasses may require access to the API.
    """

    def __init__(
        self,
        field: "RatingField",
        raw_value: Optional[Union[int, float]] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize a RatingRowValue object.

        :param field: The associated RatingField object.
        :param raw_value: The raw numerical value as fetched/returned from the API. Default is None.
        :param client: The Baserow class API client. Some RowValue subclasses may require access to the API. Default is None.
        :raises InvalidRowValueError: If the provided field is not an instance of the RatingField class.
        """
        super().__init__(field, raw_value, client)
        if not isinstance(field, RatingField):
            raise InvalidRowValueError(
                f"The provided field is not an instance of the RatingField class. Received: {type(field).__name__}"
            )
        self.logger.debug(
            f"Initialized RatingRowValue with field {self.field.name} and value {self._raw_value}"
        )

    @property
    def value(self) -> Union[int, float]:
        """
        Get the value in a user-friendly format.
        For RatingRowValue, this returns the raw value directly as it's already user-friendly.

        :return: The numerical value.
        """
        return self._raw_value

    @value.setter
    def value(self, new_value: Union[int, float]) -> None:
        """
        Set a new value.
        This should handle validation specific to RatingRowValue using the associated RatingField's validate_value method.

        :param new_value: The new numerical value to set.
        :raises InvalidRowValueError: If the value is not valid as per the associated RatingField's validation.
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
