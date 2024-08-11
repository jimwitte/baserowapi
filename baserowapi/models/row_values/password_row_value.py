from typing import Optional, Union, List, Any
from baserowapi.models.fields.field import Field
from baserowapi.models.row_values.row_value import RowValue


class PasswordRowValue(RowValue):
    """
    Represents a row value for a password field.

    :param field: The associated Field object.
    :param raw_value: The raw value as fetched/returned from the API. Defaults to None.
    :param client: The Baserow class API client. Defaults to None.
    """

    def __init__(
        self,
        field: "Field",
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ) -> None:
        super().__init__(field, raw_value, client)
        self._password_set = raw_value == "true"

    @property
    def value(self) -> bool:
        """
        Retrieve the value indicating whether the password is set.

        :return: True if the password is set, otherwise False.
        """
        return self._password_set

    @value.setter
    def value(self, new_value: Any) -> None:
        """
        Set a new password value or unset the password.

        :param new_value: The new password value or None to unset.
        :raises ValueError: If the new value is not a string or None.
        """
        if new_value is None:
            self._raw_value = None
            self._password_set = False
        elif not isinstance(new_value, str):
            raise ValueError(
                f"Expected a string or None for PasswordRowValue but got {type(new_value).__name__}"
            )
        else:
            self._raw_value = new_value
            self._password_set = True
