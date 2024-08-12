from typing import Optional, Union, List, Any
from baserowapi.models.fields import TableLinkField
from baserowapi.models.row_values.row_value import RowValue
from baserowapi.exceptions import InvalidRowValueError, FieldValidationError


class TableLinkRowValue(RowValue):
    """
    Represents a RowValue designed for a TableLinkField.

    :param field: The associated TableLinkField object.
    :param raw_value: The raw value as fetched/returned from the API. Defaults to None.
    :param client: The Baserow class API client. Some RowValue subclasses might need this. Defaults to None.
    :raises InvalidRowValueError: If the provided field is not an instance of the TableLinkField class.
    """

    def __init__(
        self,
        field: "TableLinkField",
        raw_value: Optional[List[Union[int, str]]] = None,
        client: Optional[Any] = None,
    ) -> None:
        super().__init__(field, raw_value, client)
        if not isinstance(field, TableLinkField):
            raise InvalidRowValueError(
                f"The provided field is not an instance of the TableLinkField class. Received: {type(field).__name__}"
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
    def value(self, new_value: Union[int, str, List[Union[int, str]]]) -> None:
        """
        Set a new value for TableLinkRowValue. Accepts a string, an integer, or a list of these.

        This method relies on the `validate_value` method from the associated `TableLinkField` to ensure the
        new value is correctly formatted and valid before assignment.

        :param new_value: The new value(s) to be set.
        :type new_value: Union[int, str, List[Union[int, str]]]
        :raises InvalidRowValueError: If the provided value is not in the expected format.
        """
        # Use the field's validation method
        try:
            self.field.validate_value(new_value)
        except FieldValidationError as e:
            self.logger.error(f"Validation error for value '{new_value}': {e}")
            raise InvalidRowValueError(f"Invalid value provided: {e}")

        # Format the value using the field's format_for_api method before assigning
        try:
            self._raw_value = [
                {"value": val} for val in self.field.format_for_api(new_value)
            ]
        except Exception as e:
            self.logger.error(f"Error formatting value '{new_value}' for API: {e}")
            raise InvalidRowValueError(f"Error formatting value '{new_value}': {e}")
