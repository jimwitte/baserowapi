from typing import Any, Dict
from baserowapi.models.fields.field import Field


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
        Validate the value for a text-based Field.

        :param value: The value to be validated.
        :raises ValueError: If the value is not of type `str`.
        """
        if value is None:
            return
        elif not isinstance(value, str):
            raise ValueError(
                f"Expected a string value for {type(self).__name__} but got {type(value)}"
            )
