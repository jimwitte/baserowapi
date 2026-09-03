from typing import Any, Dict
import logging
from baserowapi.models.fields.base_date_field import BaseDateField


class DateField(BaseDateField):
    """
    Represents a date-only field in Baserow.

    :ivar TYPE: The type of the field, which is 'date'.
    :vartype TYPE: str
    """

    TYPE = "date"
    def __init__(self, name: str, field_data: Dict[str, Any], client=None) -> None:
        """
        Initialize a DateField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        :param client: The Baserow API client. Defaults to None.
        :type client: Optional[Any]
        """
        super().__init__(name, field_data, client)
        self.logger = logging.getLogger(__name__)
