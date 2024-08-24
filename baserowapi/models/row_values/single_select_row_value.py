from typing import Optional, Union, List, Any
from baserowapi.models.fields import SingleSelectField
from baserowapi.models.row_values.row_value import RowValue
from baserowapi.exceptions import InvalidRowValueError


class SingleSelectRowValue(RowValue):
    """
    Represents a RowValue specifically designed for a SingleSelectField.

    Attributes:
        field (:class:`SingleSelectField`): The associated SingleSelectField object.
        raw_value (Optional[dict]): The raw value as fetched/returned from the API.
        client (Optional[Any]): The Baserow class API client. Some RowValue subclasses may require access to the API.
    """

    def __init__(
        self,
        field: "SingleSelectField",
        raw_value: Optional[dict] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize a SingleSelectRowValue object.

        :param field: The associated SingleSelectField object.
        :param raw_value: The raw value as fetched/returned from the API. Default is None.
        :param client: The Baserow class API client. Some RowValue subclasses may require access to the API. Default is None.
        """
        super().__init__(field, raw_value, client)
        if not isinstance(field, SingleSelectField):
            raise InvalidRowValueError(
                f"The provided field is not an instance of the SingleSelectField class. Received: {type(field).__name__}"
            )

    @property
    def options(self) -> List[str]:
        """
        Get a list of available option values for the associated SingleSelectField.

        :return: A list of available option values.
        :rtype: List[str]
        :raises AttributeError: If the associated field does not have the "options" attribute.
        """
        try:
            return self.field.options
        except AttributeError:
            msg = f"The associated field {self.field.name} does not have the 'options' attribute."
            self.logger.error(msg)
            raise AttributeError(msg)

    @property
    def value(self) -> str:
        """
        Get the value in a user-friendly format.
        For SingleSelectRowValue, this returns the option's text or "None" if no option is selected.

        :return: The selected option's text or "None" if no option is selected.
        """
        if self._raw_value is None:
            return None
        else:
            return self._raw_value.get("value", "None")

    @value.setter
    def value(self, new_value: Union[int, str]) -> None:
        """
        Set a new value.
        This uses the field's validate_value method to ensure the value is valid.

        :param new_value: The new value to be set, which can be either an ID or a string corresponding to an option value.
        :raises FieldValidationError: If the provided value doesn't match any select option by ID or value.
        """
        self.field.validate_value(new_value)
        option = self.field._get_option_by_id_or_value(new_value)

        self._raw_value = {
            "id": option["id"],
            "value": option["value"],
        }
