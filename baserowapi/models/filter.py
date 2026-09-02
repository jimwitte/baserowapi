from enum import Enum
from typing import Any

from baserowapi.exceptions import InvalidFieldNameError, InvalidOperatorError


class FilterCompatibility(str, Enum):
    """The package's advisory knowledge of a field/operator combination."""

    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    UNKNOWN = "unknown"


# Operators observed in generated API documentation for the configured hosted
# database. An operator outside this set is new to this package, not invalid.
KNOWN_FILTER_OPERATORS = frozenset(
    {
        "boolean",
        "contains",
        "contains_not",
        "contains_word",
        "date_after",
        "date_after_days_ago",
        "date_after_or_equal",
        "date_after_today",
        "date_before",
        "date_before_or_equal",
        "date_before_today",
        "date_equal",
        "date_equals_day_of_month",
        "date_equals_days_ago",
        "date_equals_month",
        "date_equals_months_ago",
        "date_equals_today",
        "date_equals_week",
        "date_equals_year",
        "date_equals_years_ago",
        "date_is",
        "date_is_after",
        "date_is_before",
        "date_is_not",
        "date_is_on_or_after",
        "date_is_on_or_before",
        "date_is_within",
        "date_not_equal",
        "date_within_days",
        "date_within_months",
        "date_within_weeks",
        "doesnt_contain_word",
        "empty",
        "equal",
        "filename_contains",
        "files_lower_than",
        "has_empty_value",
        "has_file_type",
        "has_not_empty_value",
        "has_not_value_contains",
        "has_not_value_contains_word",
        "has_not_value_equal",
        "has_value_contains",
        "has_value_contains_word",
        "has_value_equal",
        "has_value_length_is_lower_than",
        "higher_than",
        "higher_than_or_equal",
        "is_even_and_whole",
        "length_is_lower_than",
        "link_row_contains",
        "link_row_has",
        "link_row_has_not",
        "link_row_not_contains",
        "lower_than",
        "lower_than_or_equal",
        "multiple_collaborators_has",
        "multiple_collaborators_has_not",
        "multiple_select_has",
        "multiple_select_has_not",
        "not_empty",
        "not_equal",
        "single_select_equal",
        "single_select_is_any_of",
        "single_select_is_none_of",
        "single_select_not_equal",
        "starts_with",
    }
)


class Filter:
    """One structurally valid Baserow row filter."""

    def __init__(self, field_name: str, value: Any, operator: str = "equal"):
        if not isinstance(field_name, str) or not field_name.strip():
            raise InvalidFieldNameError("field_name must be a non-empty string.")
        if not isinstance(operator, str) or not operator.strip():
            raise InvalidOperatorError("operator must be a non-empty string.")

        self.field_name = field_name
        self.value = value
        self.operator = operator
