from typing import Any, Dict
from baserowapi.models.fields.field import Field
from baserowapi.exceptions import FieldValidationError


class PasswordField(Field):
    """
    Represents a password field in Baserow.

    :ivar TYPE: The type of the field, which is 'password'.
    :vartype TYPE: str
    """

    TYPE = "password"

    def __init__(self, name: str, field_data: Dict[str, Any], client=None) -> None:
        super().__init__(name, field_data, client)

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