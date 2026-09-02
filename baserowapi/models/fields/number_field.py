from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Union
import logging
from baserowapi.models.fields.field import Field
from baserowapi.exceptions import FieldValidationError


class NumberField(Field):
    """
    Represents a number field in Baserow.

    :ivar TYPE: The type of the field, which is 'number'.
    :vartype TYPE: str
    """

    TYPE = "number"
    _COMPATIBLE_FILTERS = [
        "equal",
        "not_equal",
        "contains",
        "contains_not",
        "higher_than",
        "higher_than_or_equal",
        "lower_than",
        "lower_than_or_equal",
        "is_even_and_whole",
        "empty",
        "not_empty",
    ]

    def __init__(self, name: str, field_data: Dict[str, Any], client=None) -> None:
        """
        Initialize a NumberField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        :param client: The Baserow API client. Defaults to None.
        :type client: Optional[Any]
        """
        super().__init__(name, field_data, client)
        self.logger = logging.getLogger(__name__)

        # Retrieve the number of decimal places allowed for this field
        self.number_decimal_places = field_data.get("number_decimal_places", 0)

        # Check if negative numbers are allowed for this field
        self.number_negative = field_data.get("number_negative", True)

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this NumberField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS

    @property
    def decimal_places(self) -> int:
        """
        Get the number of decimal places allowed for this NumberField.

        :return: The number of decimal places.
        :rtype: int
        """
        return self.number_decimal_places

    @property
    def allow_negative(self) -> bool:
        """
        Determine if the NumberField allows negative numbers.

        :return: True if negative numbers are allowed, else False.
        :rtype: bool
        """
        return self.number_negative

    def validate_value(self, value: Union[int, float, str]) -> None:
        """
        Validate the value for a NumberField.

        :param value: The number value to be validated.
        :type value: Union[int, float, str]
        :raises FieldValidationError: If the value doesn't match the expected type or constraints.
        """
        if value is None:
            return

        if isinstance(value, bool) or not isinstance(value, (int, float, str)):
            raise FieldValidationError(
                f"Expected an integer, float, numeric string, or None for "
                f"NumberField but got {type(value).__name__}."
            )

        try:
            decimal_value = Decimal(str(value))
        except (InvalidOperation, ValueError) as error:
            raise FieldValidationError(
                f"Expected a numeric value for NumberField but got {value!r}."
            ) from error

        if not decimal_value.is_finite():
            raise FieldValidationError("NumberField values must be finite numbers.")

        decimal_places = max(0, -decimal_value.as_tuple().exponent)
        if decimal_places > self.number_decimal_places:
            raise FieldValidationError(
                f"Value for NumberField exceeds the configured "
                f"{self.number_decimal_places} decimal places."
            )

        if not self.number_negative and decimal_value < 0:
            raise FieldValidationError(
                "Negative values are not allowed for this NumberField."
            )
