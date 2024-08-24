from typing import Any, Dict
from baserowapi.models.fields.field import Field
from baserowapi.exceptions import FieldValidationError


class BaseTextClass(Field):
    """A base class for text-based fields in Baserow."""

    def __init__(self, name: str, field_data: Dict[str, Any], client=None) -> None:
        """
        Initialize a BaseTextClass object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's attributes.
        :type field_data: Dict[str, Any]
        :param client: The Baserow API client. Defaults to None.
        :type client: Optional[Any]
        """
        super().__init__(name, field_data, client)

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
