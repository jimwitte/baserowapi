from typing import Any, Dict, List, Union, Iterator, Union, Optional
from baserowapi.models.fields.field import Field


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
        Validate the value for a PasswordField. Ensure it's a string or None.
        :param value: The value to be validated.
        :type value: Any
        :raises ValueError: If the value is not a string or None.
        """
        if value is not None and not isinstance(value, str):
            raise ValueError(
                f"Expected a string or None for PasswordField but got {type(value)}"
            )
