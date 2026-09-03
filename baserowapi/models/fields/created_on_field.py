from typing import Any, Dict
import logging
from baserowapi.models.fields.base_date_field import BaseDateField


class CreatedOnField(BaseDateField):
    """
    Represents a field in Baserow that indicates the creation date.

    :ivar TYPE: The type of the field, which is 'created_on'.
    :vartype TYPE: str
    """

    TYPE = "created_on"
    def __init__(self, name: str, field_data: Dict[str, Any], client=None) -> None:
        """
        Initialize a CreatedOnField object.

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
    def is_read_only(self) -> bool:
        """
        Determine if the CreatedOnField is read-only.

        :return: True, as this field type is always read-only.
        :rtype: bool
        """
        return True
