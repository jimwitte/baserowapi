from typing import Optional, Any
from baserowapi.models.fields.field import Field
from baserowapi.models.row_values.row_value import RowValue
from baserowapi.exceptions import InvalidRowValueError


class PasswordRowValue(RowValue):
    """
    Represents a row value for a password field.

    :param field: The associated Field object.
    :param raw_value: The raw value as fetched/returned from the API. Defaults to None.
    :param client: The Baserow class API client. Defaults to None.
    :raises InvalidRowValueError: If the new value is not valid as per the associated Field's validation.
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
        return self._raw_value is not None

    @value.setter
    def value(self, new_value: Any) -> None:
        """
        Set a new password value or unset the password.

        :param new_value: The new password value or None to unset.
        :raises InvalidRowValueError: If the new value is not valid as per the associated Field's validation.
        """
        try:
            self.field.validate_value(new_value)
            self._raw_value = new_value
            self._password_set = new_value is not None
            self.logger.debug(f"Set new password value for field {self.field.name}")
        except Exception as e:
            self.logger.error(
                f"Failed to set password value for field {self.field.name}. Error: {e}"
            )
            raise InvalidRowValueError(
                f"Failed to set password value for field {self.field.name}. Error: {e}"
            )
