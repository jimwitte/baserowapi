from typing import Any
from baserowapi.models.fields.field import Field
from baserowapi.exceptions import FieldValidationError


class BaseTextClass(Field):
    """A base class for text-based fields in Baserow."""

    _COMPATIBLE_FILTERS = (
        "equal",
        "not_equal",
        "contains",
        "contains_not",
        "contains_word",
        "doesnt_contain_word",
        "starts_with",
        "length_is_lower_than",
        "empty",
        "not_empty",
    )

    def validate_value(self, value: Any) -> None:
        """
        Validate the value for a TextField.

        :param value: The value to be validated.
        :type value: Any
        :raises FieldValidationError: If the value is not a valid string or None.
        """
        if value is not None and not isinstance(value, str):
            self.logger.error(
                f"Expected a string or None for text_default but got {type(value)}"
            )
            raise FieldValidationError(
                f"Expected a string or None for text_default but got {type(value)}"
            )
