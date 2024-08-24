from typing import Optional, Union, List, Any
from baserowapi.models.fields import MultipleSelectField
from baserowapi.models.row_values.row_value import RowValue
from baserowapi.exceptions import InvalidRowValueError, RowValueOperationError


class MultipleSelectRowValue(RowValue):
    """
    Represents a RowValue designed for a MultipleSelectField.

    :param field: The associated MultipleSelectField object.
    :param raw_value: The raw values as fetched/returned from the API. Defaults to None.
    :param client: The Baserow class API client. Some RowValue subclasses might need this. Defaults to None.
    :raises InvalidRowValueError: If the provided field is not an instance of the MultipleSelectField class.
    """

    def __init__(
        self,
        field: "MultipleSelectField",
        raw_value: List[Optional[Any]] = None,
        client: Optional[Any] = None,
    ) -> None:
        super().__init__(field, raw_value, client)
        if not isinstance(field, MultipleSelectField):
            raise InvalidRowValueError(
                f"The provided field is not an instance of the MultipleSelectField class. Received: {type(field).__name__}"
            )
        self._raw_value = raw_value if raw_value is not None else []

    @property
    def options(self) -> List[str]:
        """
        Get a list of available option values for the associated MultipleSelectField.

        :return: A list of available option values.
        :rtype: List[str]
        :raises RowValueOperationError: If the associated field does not have the "options" attribute.
        """
        try:
            return self.field.options
        except AttributeError:
            msg = f"The associated field {self.field.name} does not have the 'options' attribute."
            self.logger.error(msg)
            raise RowValueOperationError(msg)

    @property
    def value(self) -> List[str]:
        """
        Get the values in a user-friendly format. This method returns a list of option names.

        :return: A list of the selected option names.
        :rtype: List[str]
        """
        options = self._raw_value
        return [option["value"] for option in options if option]

    @value.setter
    def value(self, new_values: Union[List[int], List[str]]) -> None:
        """
        Set new values. This method handles validation specific to MultipleSelectRowValue.

        :param new_values: The new values to be set.
        :type new_values: Union[List[int], List[str]]
        :raises RowValueOperationError: If one of the values doesn't match any select option or other errors occur.
        """
        if not isinstance(new_values, list):
            raise RowValueOperationError("The provided values should be a list.")

        option_dicts = []

        for new_value in new_values:
            if isinstance(new_value, (int, str)):
                option = self.field._get_option_by_id_or_value(new_value)
                if option:
                    option_dicts.append(option)
                else:
                    raise RowValueOperationError(
                        f"The value '{new_value}' doesn't match any select option."
                    )
            else:
                raise RowValueOperationError(
                    f"Invalid type '{type(new_value).__name__}' for value. Expected int or str."
                )

        self._raw_value = option_dicts
