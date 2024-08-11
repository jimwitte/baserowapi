from typing import Any, Dict, List, Optional
from baserowapi.models.fields.field import Field


class LookupField(Field):
    """
    Represents a field connected to a link to table field which returns an array of values and row ids from the chosen
    lookup field in the linked table.

    :ivar TYPE: The type of the field, which is 'lookup'.
    :vartype TYPE: str
    """

    TYPE = "lookup"
    _COMPATIBLE_FILTERS = [
        "has_empty_value",
        "has_not_empty_value",
        "has_value_equal",
        "has_not_value_equal",
        "has_value_contains",
        "has_not_value_contains",
        "has_value_contains_word",
        "has_not_value_contains_word",
        "has_value_length_is_lower_than",
    ]

    def __init__(self, name: str, field_data: Dict[str, Any], client=None) -> None:
        """
        Initializes a LookupField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        :param client: The Baserow API client. Defaults to None.
        :type client: Optional[Any]
        :raises ValueError: If the field is not read-only.
        """
        super().__init__(name, field_data, client)

        if not self.is_read_only:
            self.logger.error("LookupField should be read-only.")
            raise ValueError("LookupField should be read-only.")

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this LookupField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS

    @property
    def through_field_id(self) -> Optional[int]:
        """
        Retrieve the through_field_id of the field from field_data.

        :return: The id of the linking field.
        :rtype: Optional[int]
        """
        return self.field_data.get("through_field_id", None)

    @property
    def through_field_name(self) -> Optional[int]:
        """
        Retrieve the through_field_name of the field from field_data.

        :return: The name of the linking field.
        :rtype: Optional[int]
        """
        return self.field_data.get("through_field_name", None)

    @property
    def target_field_id(self) -> Optional[int]:
        """
        Retrieve the target_field_id of the field from field_data.

        :return: The id of the target field.
        :rtype: Optional[int]
        """
        return self.field_data.get("target_field_id", None)

    @property
    def target_field_name(self) -> Optional[str]:
        """
        Retrieve the target_field_name of the field from field_data.

        :return: The name of the target field.
        :rtype: Optional[str]
        """
        return self.field_data.get("target_field_name", None)
