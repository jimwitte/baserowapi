from typing import Any, Dict, List, Union, Optional
import logging
from baserowapi.models.fields.field import Field
from baserowapi.exceptions import FieldValidationError


class MultipleSelectField(Field):
    """
    Represents a multiple-select field allowing the user to select multiple options from a predefined set of options.

    :ivar TYPE: The type of the field, which is 'multiple_select'.
    :vartype TYPE: str
    """

    TYPE = "multiple_select"
    _COMPATIBLE_FILTERS = [
        "contains",
        "contains_not",
        "contains_word",
        "doesnt_contain_word",
        "multiple_select_has",
        "multiple_select_has_not",
        "empty",
        "not_empty",
    ]

    def __init__(self, name: str, field_data: Dict[str, Any], client=None) -> None:
        """
        Initialize a MultipleSelectField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        :param client: The Baserow API client. Defaults to None.
        :type client: Optional[Any]
        """
        super().__init__(name, field_data, client)
        self.logger = logging.getLogger(__name__)
        if "select_options" not in field_data or not isinstance(
            field_data["select_options"], list
        ):
            self.logger.error(
                "Invalid or missing select_options provided for MultipleSelectField initialization."
            )
            raise FieldValidationError(
                "select_options should be a non-empty list in field_data."
            )

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this MultipleSelectField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS

    @property
    def options(self) -> List[str]:
        """
        Retrieve a list of select option values from the field_data.

        :return: List of select option values.
        :rtype: List[str]
        """
        return [option["value"] for option in self.field_data["select_options"]]

    @property
    def options_details(self) -> List[Dict[str, Any]]:
        """
        Retrieve a list including details like id, value, color of each select_option.

        :return: List of detailed select_options.
        :rtype: List[Dict[str, Any]]
        """
        return self.field_data["select_options"]

    def _get_option_by_id_or_value(
        self, value: Union[int, str]
    ) -> Optional[Dict[str, Any]]:
        """
        Utility method to retrieve an option by its id or value.

        :param value: The id or value of the option to retrieve.
        :type value: Union[int, str]
        :return: The option if found, otherwise None.
        :rtype: Optional[Dict[str, Any]]
        """
        for option in self.options_details:
            if option["id"] == value or option["value"] == value:
                return option
        return None

    def validate_value(self, values: List[Union[int, str]]) -> None:
        """
        Validates the values for a MultipleSelectField.

        :param values: The list of values to validate.
        :type values: List[Union[int, str]]
        :raises FieldValidationError: If the provided values list contains a value that doesn't match any select option.
        """
        if values is None:
            return

        if not isinstance(values, list):
            raise FieldValidationError(
                "The provided value should be a list for a MultipleSelectField."
            )

        for value in values:
            option = self._get_option_by_id_or_value(value)
            if not option:
                raise FieldValidationError(
                    f"The provided value '{value}' doesn't match any select option."
                )
