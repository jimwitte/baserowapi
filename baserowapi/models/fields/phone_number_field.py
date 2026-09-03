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
    _VALID_CHARACTERS = re.compile(r"^[0-9 Nx,._+*()#=;/-]{1,100}$")
    _COMPATIBLE_FILTERS = (
        "equal",
        "not_equal",
        "contains",
        "contains_not",
        "starts_with",
        "length_is_lower_than",
        "empty",
        "not_empty",
    )

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
        if not self._VALID_CHARACTERS.match(value):
            raise FieldValidationError(
                "The provided phone number doesn't match Baserow's expected format."
            )
