from typing import Optional, Any
import logging
from baserowapi.models.fields.field import Field


class RowValue:
    """
    Represents a value in a Baserow row associated with a specific field.

    Attributes:
        field (:class:`Field`): The associated Field object.
        _raw_value (Optional[Any]): The raw value as returned/fetched from the API.
        logger (logging.Logger): Logger instance for the class.
    """

    def __init__(
        self,
        field: "Field",
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize a RowValue object.

        :param field: The associated Field object.
        :param raw_value: The raw value as returned/fetched from the API.
        :param client: The Baserow class API client. Some child classes of RowValue need access to the API.
        :raises ValueError: If the provided field is not an instance of the Field class.
        """
        if not isinstance(field, Field):
            raise ValueError(
                f"The provided field is not an instance of the Field class. Received: {type(field).__name__}"
            )

        self.field = field
        self._raw_value = raw_value
        self.client = client
        self.logger = logging.getLogger(__name__)
        self.logger.debug(
            f"Initialized RowValue with field {self.field.name} and value {self._raw_value}"
        )

    def __repr__(self) -> str:
        """
        Provide a string representation of the RowValue object.

        :return: String representation of the Row value.
        :rtype: str
        """
        return f"Baserow row value '{self.name}' of type '{self.type}' with value '{self.value}'"

    @property
    def value(self) -> Any:
        """
        Get the value in a user-friendly format.
        By default, this returns the raw value, but child classes can override this
        for type-specific formatting or conversion.

        :return: User-friendly formatted value.
        """
        return self._raw_value

    @value.setter
    def value(self, new_value: Any) -> None:
        """
        Set a new value.
        This should handle validation and potentially conversion to a format suitable for the API.

        :param new_value: New value to set.
        :raises Exception: If the validation of the new value fails.
        """
        try:
            self.field.validate_value(new_value)
            self._raw_value = (
                new_value  # Child classes can transform this value before setting
            )
            self.logger.debug(f"Set new value {new_value} for field {self.field.name}")
        except Exception as e:
            self.logger.error(
                f"Failed to set value for field {self.field.name}. Error: {e}"
            )
            raise

    def format_for_api(self) -> Any:
        """
        Format the value for API submission by delegating to the associated Field's format_for_api method.

        :return: Formatted value for API submission.
        """
        return self.field.format_for_api(self._raw_value)

    @property
    def is_read_only(self) -> bool:
        """
        Check if the associated field is read-only.

        :return: True if the field is read-only, False otherwise.
        """
        return self.field.is_read_only

    @property
    def type(self) -> str:
        """
        Get the type of the associated field.

        :return: Type of the field.
        """
        return self.field.type

    @property
    def name(self) -> str:
        """
        Get the name of the associated field.

        :return: Name of the field.
        """
        return self.field.name
