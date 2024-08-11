from typing import Any, Dict, List
import logging
from baserowapi.models.fields.base_date_field import BaseDateField


class LastModifiedField(BaseDateField):
    """
    Represents a field in Baserow that indicates the last modified date.

    :ivar TYPE: The type of the field, which is 'last_modified'.
    :vartype TYPE: str
    """

    TYPE = "last_modified"
    _COMPATIBLE_FILTERS = [
        "date_equal",
        "date_not_equal",
        "date_equals_today",
        "date_before_today",
        "date_after_today",
        "date_within_days",
        "date_within_weeks",
        "date_within_months",
        "date_equals_days_ago",
        "date_equals_months_ago",
        "date_equals_years_ago",
        "date_equals_week",
        "date_equals_month",
        "date_equals_year",
        "date_equals_day_of_month",
        "date_before",
        "date_before_or_equal",
        "date_after",
        "date_after_or_equal",
        "date_after_days_ago",
        "contains",
        "contains_not",
        "empty",
        "not_empty",
    ]

    def __init__(self, name: str, field_data: Dict[str, Any], client=None) -> None:
        """
        Initialize a LastModifiedField object.

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
        Get the list of compatible filters for this LastModifiedField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS

    @property
    def is_read_only(self) -> bool:
        """
        Determine if the LastModifiedField is read-only.

        :return: True, as this field type is always read-only.
        :rtype: bool
        """
        return True
