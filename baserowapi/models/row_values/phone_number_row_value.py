from typing import Optional, Any
from baserowapi.models.fields import PhoneNumberField
from baserowapi.models.row_values.row_value import RowValue


class PhoneNumberRowValue(RowValue):
    """
    Represents a RowValue specifically designed for a PhoneNumberField.

    Attributes:
        field (:class:`PhoneNumberField`): The associated PhoneNumberField object.
        raw_value (Optional[Any]): The raw value as fetched/returned from the API.
        client (Optional[Any]): The Baserow class API client. Some RowValue subclasses may require access to the API.
    """

    def __init__(
        self,
        field: "PhoneNumberField",
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize a PhoneNumberRowValue object.

        :param field: The associated PhoneNumberField object.
        :param raw_value: The raw value as fetched/returned from the API. Default is None.
        :param client: The Baserow class API client. Some RowValue subclasses may require access to the API. Default is None.
        """
        super().__init__(field, raw_value, client)
        if not isinstance(field, PhoneNumberField):
            raise ValueError(
                f"The provided field is not an instance of the PhoneNumberField class. Received: {type(field).__name__}"
            )
        self.logger.debug(
            f"Initialized PhoneNumberRowValue with field {self.field.name} and value {self._raw_value}"
        )
