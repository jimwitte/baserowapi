from typing import Optional, Any
from baserowapi.models.fields import FormulaField
from baserowapi.models.row_values.row_value import RowValue
from baserowapi.exceptions import InvalidRowValueError, ReadOnlyValueError


class FormulaRowValue(RowValue):
    """
    Represents a RowValue designed for a FormulaField.

    :param field: The associated FormulaField object.
    :param raw_value: The raw value as fetched/returned from the API. Defaults to None.
    :param client: The Baserow class API client. Some RowValue subclasses might need this. Defaults to None.
    :raises InvalidRowValueError: If the provided field is not an instance of the FormulaField class.
    """

    def __init__(
        self,
        field: "FormulaField",
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ) -> None:
        super().__init__(field, raw_value, client)
        if not isinstance(field, FormulaField):
            raise InvalidRowValueError(
                f"The provided field is not an instance of the FormulaField class. Received: {type(field).__name__}"
            )

    @property
    def value(self) -> Any:
        """
        Get the value in a user-friendly format. This method returns the raw value.

        :return: The raw value of the FormulaRowValue.
        :rtype: Any
        """
        return self._raw_value

    @value.setter
    def value(self, new_value: Any) -> None:
        """
        Set a new value. As FormulaRowValue is read-only, this method raises an error.

        :param new_value: The new value to be set.
        :raises ReadOnlyValueError: As the FormulaRowValue is read-only, setting a value will always raise this error.
        """
        raise ReadOnlyValueError("Cannot set value for a read-only FormulaRowValue.")
