from typing import Any, Dict, List
from baserowapi.models.fields.base_text_class import BaseTextClass


class UrlField(BaseTextClass):
    """
    Represents a URL field in Baserow.

    :ivar TYPE: The type of the field, which is 'url'.
    :vartype TYPE: str
    """

    TYPE = "url"
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
        Initialize a UrlField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        :param client: The Baserow API client. Defaults to None.
        :type client: Optional[Any]
        """
        super().__init__(name, field_data, client)

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this UrlField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS
