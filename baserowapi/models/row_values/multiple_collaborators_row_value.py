from typing import Optional, Any
from baserowapi.models.fields import MultipleCollaboratorsField
from baserowapi.models.row_values.row_value import RowValue


class MultipleCollaboratorsRowValue(RowValue):
    """
    Represents a RowValue designed for a MultipleCollaboratorsField.

    :param field: The associated MultipleCollaboratorsField object.
    :param raw_value: The raw value as fetched/returned from the API. Defaults to None.
    :param client: The Baserow class API client. Some RowValue subclasses might need this. Defaults to None.
    :raises ValueError: If the provided field is not an instance of the MultipleCollaboratorsField class.
    """

    def __init__(
        self,
        field: "MultipleCollaboratorsField",
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ) -> None:
        super().__init__(field, raw_value, client)
        if not isinstance(field, MultipleCollaboratorsField):
            raise ValueError(
                f"The provided field is not an instance of the MultipleCollaboratorsField class. Received: {type(field).__name__}"
            )

    @property
    def value(self) -> Any:
        """
        Get the value in a user-friendly format. This method returns the raw value.

        :return: The raw value.
        :rtype: Any
        """
        return self._raw_value

    @value.setter
    def value(self, new_value: Any) -> None:
        """
        Validate and set the new value for MultipleCollaboratorsRowValue.

        :param new_value: The new value to be set.
        :raises ValueError: If the new value is not valid.
        """
        self.field.validate_value(new_value)
        self._raw_value = new_value
