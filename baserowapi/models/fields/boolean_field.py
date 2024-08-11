from typing import Any, Dict, List
import logging
from baserowapi.models.fields.field import Field


class BooleanField(Field):
    """
    Represents a boolean field in Baserow.

    :ivar TYPE: The type of the field, which is 'boolean'.
    :vartype TYPE: str
    """

    TYPE = "boolean"
    _COMPATIBLE_FILTERS = ["boolean", "empty", "not_empty"]

    def __init__(self, name: str, field_data: Dict[str, Any], client=None) -> None:
        """
        Initialize a BooleanField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        :param client: The Baserow API client. Defaults to None.
        :type client: Optional[Any]
        """
        super().__init__(name, field_data, client)
        self.logger = logging.getLogger(__name__)

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this BooleanField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS

    def validate_value(self, value: bool) -> None:
        """
        Validate the value for a BooleanField.

        :param value: The boolean value to be validated.
        :type value: bool
        :raises ValueError: If the value is not of boolean type.
        """
        if not isinstance(value, bool):
            self.logger.error(
                f"Expected a boolean value for BooleanField but got {type(value)}"
            )
            raise ValueError(
                f"Expected a boolean value for BooleanField but got {type(value)}"
            )
