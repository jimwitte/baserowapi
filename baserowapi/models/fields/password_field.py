from typing import Any
from baserowapi.models.fields.field import Field
from baserowapi.exceptions import FieldValidationError, FieldValueError


class PasswordField(Field):
    """
    Represents a password field in Baserow.

    :ivar TYPE: The type of the field, which is 'password'.
    :vartype TYPE: str
    """

    TYPE = "password"

    def validate_value(self, value: Any) -> None:
        """
        Validate the value for a PasswordField. Ensure it's a string, None, or True.

        :param value: The value to be validated.
        :type value: Any
        :raises FieldValidationError: If the value is not a string, None, or True.
        """
        if not (value is None or isinstance(value, str) or value is True):
            raise FieldValidationError(
                f"Expected a string, None, or True for PasswordField but got {type(value)}"
            )

    def decode_value(self, raw_value: Any) -> Any:
        """Preserve Baserow's ``True`` or ``None`` password read state."""
        if raw_value is not True and raw_value is not None:
            raise FieldValueError(
                "A password response must be True or None."
            )
        return raw_value

    def is_set(self, raw_value: Any) -> bool:
        """Return whether a hosted password read indicates a set password."""
        return self.decode_value(raw_value) is True
