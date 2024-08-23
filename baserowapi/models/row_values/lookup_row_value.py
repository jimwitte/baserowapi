from typing import Optional, Any, List, Union
from baserowapi.models.fields import LookupField
from baserowapi.models.row_values.row_value import RowValue
from baserowapi.exceptions import InvalidRowValueError, ReadOnlyValueError


class LookupRowValue(RowValue):
    """
    Represents a RowValue designed for a LookupField.

    :param field: The associated LookupField object.
    :param raw_value: The raw value as fetched/returned from the API, representing an array of values and row IDs. Defaults to None.
    :param client: The Baserow class API client. Some RowValue subclasses might need this. Defaults to None.
    :raises InvalidRowValueError: If the provided field is not an instance of the LookupField class.
    """

    def __init__(
        self,
        field: "LookupField",
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ) -> None:
        super().__init__(field, raw_value, client)
        if not isinstance(field, LookupField):
            raise InvalidRowValueError(
                f"The provided field is not an instance of the LookupField class. Received: {type(field).__name__}"
            )

    @property
    def value(self) -> List[Union[int, str]]:
        """
        Get the value in a user-friendly format. This method returns a list of primary field values or IDs.

        :return: A list of primary field values or IDs.
        :rtype: List[Union[int, str]]
        """
        return [entry.get("value", entry.get("id", "")) for entry in self._raw_value]

    @value.setter
    def value(self, new_value: Any) -> None:
        """
        Set a new value for LookupRowValue. Since LookupRowValue is read-only, setting a value will raise an error.

        :param new_value: The new value to be set.
        :raises ReadOnlyValueError: As the LookupRowValue is read-only, setting a value will always raise an error.
        """
        raise ReadOnlyValueError("Cannot set value for a read-only LookupRowValue.")
