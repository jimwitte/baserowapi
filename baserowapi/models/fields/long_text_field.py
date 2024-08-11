from typing import Any, Dict, List
from baserowapi.models.fields.base_text_class import BaseTextClass


class LongTextField(BaseTextClass):
    """
    Represents a long text field in Baserow.

    :ivar TYPE: The type of the field, which is 'long_text'.
    :vartype TYPE: str
    """

    TYPE = "long_text"
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
        Initialize a LongTextField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        :param client: The Baserow API client. Defaults to None.
        :type client: Optional[Any]
        :raises ValueError: If the 'text_default' value in field_data is not a string or
                            if the 'long_text_enable_rich_text' value in field_data is not a boolean.
        """
        super().__init__(name, field_data, client)

        text_default_value = field_data.get("text_default", "")
        self.validate_value(text_default_value)
        self._text_default = text_default_value

        long_text_enable_rich_text_value = field_data.get(
            "long_text_enable_rich_text", False
        )
        if not isinstance(long_text_enable_rich_text_value, bool):
            raise ValueError(
                f"Expected a boolean value for long_text_enable_rich_text but got {type(long_text_enable_rich_text_value)}"
            )
        self._long_text_enable_rich_text = long_text_enable_rich_text_value

    @property
    def text_default(self) -> str:
        """
        Get the default text value for this LongTextField.

        :return: The default text value.
        :rtype: str
        """
        return self._text_default

    @property
    def long_text_enable_rich_text(self) -> bool:
        """
        Get the rich text enable status for this LongTextField.

        :return: The rich text enable status.
        :rtype: bool
        """
        return self._long_text_enable_rich_text

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this LongTextField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS
