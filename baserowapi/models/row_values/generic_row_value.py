from typing import Optional, Any
from baserowapi.models.fields import GenericField
from baserowapi.models.row_values.row_value import RowValue


class GenericRowValue(RowValue):
    """
    Represents a RowValue for an unsupported or generic field type.

    :param field: The associated GenericField object.
    :param raw_value: The raw value as fetched/returned from the API. Defaults to None.
    :param client: The Baserow class API client. Defaults to None.
    :raises ValueError: If the provided field is not an instance of the GenericField class.
    """

    def __init__(
        self,
        field: "GenericField",
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ) -> None:
        super().__init__(field, raw_value, client)
        if not isinstance(field, GenericField):
            raise ValueError(
                f"The provided field is not an instance of the GenericField class. Received: {type(field).__name__}"
            )

        self.logger.warning(
            f"Initialized a generic row value for field '{self.field.name}' of unsupported type."
        )

    @property
    def value(self) -> Any:
        """
        Retrieve the value of the GenericRowValue.

        :return: The raw value.
        """
        return self._raw_value

    @value.setter
    def value(self, new_value: Any) -> None:
        """
        Set a new value for the GenericRowValue.

        :param new_value: The new value to set.
        """
        self.field.validate_value(new_value)
        self._raw_value = new_value
