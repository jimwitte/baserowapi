from typing import Optional, Any
from baserowapi.models.fields import CountField
from baserowapi.models.row_values.row_value import RowValue
from baserowapi.exceptions import InvalidRowValueError, ReadOnlyValueError


class CountRowValue(RowValue):
    """
    Represents a RowValue designed for a CountField.

    :param field: The associated CountField object.
    :param raw_value: The raw value as fetched/returned from the API, representing the main (primary) field text values of the linked rows. Defaults to None.
    :param client: The Baserow class API client. Some RowValue subclasses might need this. Defaults to None.
    :raises InvalidRowValueError: If the provided field is not an instance of the CountField class.
    """

    def __init__(
        self,
        field: "CountField",
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ) -> None:
        super().__init__(field, raw_value, client)
        if not isinstance(field, CountField):
            raise InvalidRowValueError(
                f"The provided field is not an instance of the CountField class. Received: {type(field).__name__}"
            )

    @property
    def value(self) -> Any:
        """
        Get the value in a user-friendly format. This method returns the main (primary) field text values of the linked rows.

        :return: The main (primary) field text values of the linked rows.
        :rtype: Any
        """
        return self._raw_value

    @value.setter
    def value(self, new_value: Any) -> None:
        """
        Set a new value for CountRowValue. Since CountRowValue is read-only, setting a value will raise an error.

        :param new_value: The new value to be set.
        :raises ReadOnlyValueError: As the CountRowValue is read-only, setting a value will always raise an error.
        """
        raise ReadOnlyValueError("Cannot set value for a read-only CountRowValue.")
