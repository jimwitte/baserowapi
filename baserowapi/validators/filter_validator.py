import logging
from baserowapi.models.filter import Filter
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from baserowapi.models.table import Table
    from baserowapi.models.field import Field

class FilterValidator:
    """
    FilterValidator is a utility class that provides methods for validating 
    filters against a table's field types.

    :cvar logger: Logging interface for the validator.
    :vartype logger: Logger
    """

    logger = logging.getLogger(__name__)

    @staticmethod
    def validate_filters_against_table(filters: list, table: 'Table') -> None:
        """
        Validates filters against the types of fields in the provided table.

        :param filters: List of filters to validate.
        :type filters: list
        :param table: The table against which filters are validated.
        :type table: Table
        :raises ValueError: If validation fails for any filter.
        """
        if not isinstance(filters, list):
            FilterValidator.logger.error(f"'filters' must be a list.")
            raise ValueError(f"'filters' must be a list.")
        
        FilterValidator._check_for_missing_attributes(filters)

        for filter_obj in filters:
            FilterValidator._validate_single_filter_obj(filter_obj, table)

    @staticmethod
    def _check_for_missing_attributes(filters: list) -> None:
        """
        Checks if filters have the required attributes.

        :param filters: List of filters to check.
        :type filters: list
        :raises ValueError: If any filter lacks required attributes.
        """
        for filter_obj in filters:
            if not hasattr(filter_obj, 'field_name') or not hasattr(filter_obj, 'operator'):
                FilterValidator.logger.error(f"All items in 'filters' must have 'field_name' and 'operator' attributes.")
                raise ValueError(f"All items in 'filters' must have 'field_name' and 'operator' attributes.")

    @staticmethod
    def _validate_single_filter_obj(filter_obj: Filter, table: 'Table') -> None:
        """
        Validates a single filter object.

        :param filter_obj: The filter object to validate.
        :type filter_obj: Filter
        :param table: The table against which the filter is validated.
        :type table: Table
        :raises ValueError: If validation fails for the filter.
        """
        filter_name = filter_obj.field_name
        if filter_name not in table.field_names:
            FilterValidator.logger.error(f"Invalid field name in filter: {filter_name}")
            raise ValueError(f"Invalid field name in filter: {filter_name}")

        filter_type = filter_obj.operator
        filter_value = filter_obj.value

        FilterValidator.logger.debug(f"Validating filter: field='{filter_name}', type='{filter_type}', value='{filter_value}'")
        field = table.fields[filter_name]
        if not FilterValidator._validate_single_filter(filter_type, filter_value, field):
            FilterValidator.logger.error(f"Invalid filter '{filter_type}' with value '{filter_value}' for field type '{field.TYPE}'")
            raise ValueError(f"Invalid filter '{filter_type}' with value '{filter_value}' for field type '{field.TYPE}'")

    @staticmethod
    def _validate_single_filter(filter_type: str, filter_value: 'Any', field: 'Field') -> bool:
        """
        Validates a single filter against a field.

        :param filter_type: The type of the filter being applied.
        :type filter_type: str
        :param filter_value: The value provided for the filter.
        :type filter_value: Any
        :param field: The field against which the filter is validated.
        :type field: Field
        :return: True if the filter is valid for the field, False otherwise.
        :rtype: bool
        """
        return filter_type in getattr(field, 'compatible_filters', [])
