from typing import Any, Dict, List, Optional
from baserowapi.models.fields.field import Field


class CountField(Field):
    """
    Represents a field connected to a link to table field which returns the number of relations.

    :ivar TYPE: The type of the field, which is 'count'.
    :vartype TYPE: str
    """

    TYPE = "count"
    _COMPATIBLE_FILTERS = [
        "equal",
        "not_equal",
        "contains",
        "contains_not",
        "higher_than",
        "lower_than",
        "is_even_and_whole",
        "empty",
        "not_empty",
    ]

    def __init__(self, name: str, field_data: Dict[str, Any], client=None) -> None:
        """
        Initializes a CountField object.

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
        Get the list of compatible filters for this CountField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS

    @property
    def is_read_only(self) -> bool:
        """
        Determine if the field is read-only.

        :return: Always True for CountField.
        :rtype: bool
        """
        return True

    def validate_value(self, value: int) -> None:
        """
        Validate the value for a CountField.

        :param value: The value to validate.
        :type value: int
        :raises ValueError: If the value is not an integer or if it's negative.
        """
        if not isinstance(value, int):
            raise ValueError(
                f"Expected an integer value for CountField but got {type(value)}"
            )
        if value < 0:
            raise ValueError("CountField value cannot be negative.")

    @property
    def through_field_id(self) -> Optional[str]:
        """
        Retrieve the through_field_id of the field from field_data.

        :return: The id of the linking field.
        :rtype: Optional[str]
        """
        return self.field_data.get("through_field_id", None)

    @property
    def table_id(self) -> Optional[int]:
        """
        Retrieve the table_id of the field from field_data.

        :return: The table_id of the field.
        :rtype: Optional[int]
        """
        return self.field_data.get("table_id", None)
