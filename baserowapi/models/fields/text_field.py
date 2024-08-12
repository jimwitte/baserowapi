from typing import Any, Dict, List
from baserowapi.models.fields.base_text_class import BaseTextClass


class TextField(BaseTextClass):
    """
    Represents a text field in Baserow.

    :ivar TYPE: The type of the field, which is 'text'.
    :vartype TYPE: str
    """

    TYPE = "text"

    _COMPATIBLE_FILTERS = [
        "equal",
        "not_equal",
        "contains",
        "contains_not",
        "contains_word",
        "doesnt_contain_word",
        "length_is_lower_than",
        "empty",
        "not_empty",
    ]

    def __init__(self, name: str, field_data: Dict[str, Any], client=None) -> None:
        """
        Initialize a TextField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        :param client: The Baserow API client. Defaults to None.
        :type client: Optional[Any]
        :raises FieldValidationError: If the 'text_default' value in field_data is not a valid string.
        """
        super().__init__(name, field_data, client)

        text_default_value = field_data.get("text_default", "")
        self.validate_value(text_default_value)

        self._text_default = text_default_value

    @property
    def text_default(self) -> str:
        """
        Get the default text value for this TextField.

        :return: The default text value.
        :rtype: str
        """
        return self._text_default

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this TextField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS
