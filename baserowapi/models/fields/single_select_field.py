from typing import Any, Dict, List, Union, Optional
import logging
from baserowapi.models.fields.field import Field


class SingleSelectField(Field):
    """
    Represents a single select field in Baserow.

    :ivar TYPE: The type of the field, which is 'single_select'.
    :vartype TYPE: str
    """

    TYPE = "single_select"
    _COMPATIBLE_FILTERS = [
        "contains",
        "contains_not",
        "contains_word",
        "doesnt_contain_word",
        "single_select_equal",
        "single_select_not_equal",
        "empty",
        "not_empty",
    ]

    def __init__(self, name: str, field_data: Dict[str, Any], client=None) -> None:
        """
        Initialize a SingleSelectField object.

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
                "Invalid or missing select_options provided for SingleSelectField initialization."
            )
            raise ValueError("select_options should be a non-empty list in field_data.")

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this SingleSelectField.

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

    def validate_value(self, value: Union[int, str]) -> None:
        """
        Validates the value for a SingleSelectField.

        :param value: The value to validate.
        :type value: Union[int, str]
        :raises ValueError: If the provided value doesn't match any select option.
        """
        if value is not None:
            option = self._get_option_by_id_or_value(value)
            if not option:
                raise ValueError(
                    f"The provided value '{value}' doesn't match any select option."
                )
