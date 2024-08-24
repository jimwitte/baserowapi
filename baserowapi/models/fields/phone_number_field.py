from typing import Any, Dict, List
import logging
import re
from baserowapi.models.fields.field import Field
from baserowapi.exceptions import FieldValidationError


class PhoneNumberField(Field):
    """
    Represents a phone number field in Baserow.

    :ivar TYPE: The type of the field, which is 'phone_number'.
    :vartype TYPE: str
    """

    TYPE = "phone_number"
    _COMPATIBLE_FILTERS = [
        "equal",
        "not_equal",
        "contains",
        "contains_not",
        "length_is_lower_than",
        "empty",
        "not_empty",
    ]

    def __init__(self, name: str, field_data: Dict[str, Any], client=None) -> None:
        """
        Initialize a PhoneNumberField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        :param client: The Baserow API client. Defaults to None.
        :type client: Optional[Any]
        """
        super().__init__(name, field_data, client)
        self.valid_characters = re.compile(r"^[0-9 Nx,._+*()#=;/-]{1,100}$")
        self.logger = logging.getLogger(__name__)

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this PhoneNumberField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS

    def validate_value(self, value: str) -> None:
        """
        Validate the value for a PhoneNumberField.

        Phone numbers can have a maximum length of 100 characters consisting solely of
        digits, spaces, and the characters: Nx,._+*()#=;/-.

        :param value: The phone number string to be validated.
        :type value: str
        :raises FieldValidationError: If the phone number doesn't match the expected format.
        """
        if value is None or value == "":
            return
        if not self.valid_characters.match(value):
            self.logger.error(
                f"The provided phone number '{value}' doesn't match the expected format."
            )
            raise FieldValidationError(
                f"The provided phone number '{value}' doesn't match the expected format."
            )
