
import logging
from baserowapi.models.filter import Filter

class FilterValidator:
    """
    FilterValidator is a utility class that provides methods for validating 
    filters against a table's field types.

    Attributes:
    - logger (Logger): Logging interface for the validator.
    - ALLOWED_FILTERS (dict): A mapping between field types and their allowed filters.
    """

    logger = logging.getLogger(__name__)

    ALLOWED_FILTERS = {
        "text": ["equal", "not_equal", "contains", "contains_not", "contains_word", "doesnt_contain_word", "length_is_lower_than", "empty", "not_empty"],
        "long_text": ["equal", "not_equal", "contains", "contains_not", "contains_word", "doesnt_contain_word", "length_is_lower_than", "empty", "not_empty"],
        "boolean": ["boolean", "empty", "not_empty"],
        "number": ["equal", "not_equal", "contains", "contains_not", "higher_than", "lower_than", "is_even_and_whole", "empty", "not_empty"],
        "rating": ["equal", "not_equal", "higher_than", "lower_than"],
        "date": ["date_equal", "date_not_equal", "date_equals_today", "date_before_today", "date_after_today", "date_within_days", "date_within_weeks", "date_within_months", "date_equals_days_ago", "date_equals_months_ago", "date_equals_years_ago", "date_equals_week", "date_equals_month", "date_equals_year", "date_equals_day_of_month", "date_before", "date_before_or_equal", "date_after", "date_after_or_equal", "date_after_days_ago", "contains", "contains_not", "empty", "not_empty"],
        "last_modified": ["date_equal", "date_not_equal", "date_equals_today", "date_before_today", "date_after_today", "date_within_days", "date_within_weeks", "date_within_months", "date_equals_days_ago", "date_equals_months_ago", "date_equals_years_ago", "date_equals_week", "date_equals_month", "date_equals_year", "date_equals_day_of_month", "date_before", "date_before_or_equal", "date_after", "date_after_or_equal", "date_after_days_ago", "contains", "contains_not", "empty", "not_empty"],
        "created_on": ["date_equal", "date_not_equal", "date_equals_today", "date_before_today", "date_after_today", "date_within_days", "date_within_weeks", "date_within_months", "date_equals_days_ago", "date_equals_months_ago", "date_equals_years_ago", "date_equals_week", "date_equals_month", "date_equals_year", "date_equals_day_of_month", "date_before", "date_before_or_equal", "date_after", "date_after_or_equal", "date_after_days_ago", "contains", "contains_not", "empty", "not_empty"],
        "url": ["equal", "not_equal", "contains", "contains_not", "contains_word", "doesnt_contain_word", "length_is_lower_than", "empty", "not_empty"],
        "email": ["equal", "not_equal", "contains", "contains_not", "contains_word", "doesnt_contain_word", "length_is_lower_than", "empty", "not_empty"],
        "file": ["filename_contains", "has_file_type", "empty", "not_empty"],
        "single_select": ["contains", "contains_not", "contains_word", "doesnt_contain_word", "single_select_equal", "single_select_not_equal", "empty", "not_empty"],
        "multiple_select": ["contains", "contains_not", "contains_word", "doesnt_contain_word", "multiple_select_has", "multiple_select_has_not", "empty", "not_empty"],
        "phone_number": ["equal", "not_equal", "contains", "contains_not", "length_is_lower_than", "empty", "not_empty"],
        "link_row": ["link_row_has", "link_row_has_not", "link_row_contains", "link_row_not_contains", "empty", "not_empty"],
        "count": ["equal", "not_equal", "contains", "contains_not", "higher_than", "lower_than", "is_even_and_whole", "empty", "not_empty"],
        "multiple_collaborators": ["multiple_collaborators_has", "multiple_collaborators_has_not", "empty", "not_empty"],
        "formula": [],
        "lookup": []
    }

    @staticmethod
    def validate_filters_against_table(filters, table):
        """
        Validates filters against the types of fields in the provided table.
        """

        # Check that filters is a list
        if not isinstance(filters, list):
            FilterValidator.logger.error(f"'filters' must be a list.")
            raise ValueError(f"'filters' must be a list.")
        
        # Check for missing attributes first
        FilterValidator._check_for_missing_attributes(filters)

        for filter_obj in filters:
            FilterValidator._validate_single_filter_obj(filter_obj, table)

    @staticmethod
    def _check_for_missing_attributes(filters):
        """
        Checks if filters have the required attributes.
        """
        for filter_obj in filters:
            if not hasattr(filter_obj, 'field_name') or not hasattr(filter_obj, 'operator'):
                FilterValidator.logger.error(f"All items in 'filters' must have 'field_name' and 'operator' attributes.")
                raise ValueError(f"All items in 'filters' must have 'field_name' and 'operator' attributes.")

    @staticmethod
    def _validate_single_filter_obj(filter_obj, table):
        """
        Validates a single filter object.
        """
        filter_name = filter_obj.field_name
        if filter_name not in table.get_field_names():
            FilterValidator.logger.error(f"Invalid field name in filter: {filter_name}")
            raise ValueError(f"Invalid field name in filter: {filter_name}")

        filter_type = filter_obj.operator
        filter_value = filter_obj.value

        FilterValidator.logger.debug(f"Validating filter: field='{filter_name}', type='{filter_type}', value='{filter_value}'")
        field_type = table.get_field_type(filter_name)
        if not FilterValidator._validate_single_filter(filter_type, filter_value, field_type):
            FilterValidator.logger.error(f"Invalid filter '{filter_type}' with value '{filter_value}' for field type '{field_type}'")
            raise ValueError(f"Invalid filter '{filter_type}' with value '{filter_value}' for field type '{field_type}'")

    @staticmethod
    def _validate_single_filter(filter_type, filter_value, field_type):
        """
        Validates a single filter against a field type.

        Args:
        - filter_type (str): The type of the filter being applied.
        - filter_value (Any): The value provided for the filter.
        - field_type (str): The type of the field.

        Returns:
        - bool: True if the filter is valid for the field type, False otherwise.
        """
        allowed_filters = FilterValidator.ALLOWED_FILTERS.get(field_type, [])
        
        # Add any extra validation for filter_value based on its field type here if necessary.

        return filter_type in allowed_filters
