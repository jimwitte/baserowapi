from typing import Any, Dict, List, Union
import logging
from baserowapi.models.fields.field import Field


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
        :raises ValueError: If the value doesn't match the expected type or constraints.
        """
        if value is None:
            return

        if isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                self.logger.error(
                    f"Expected a number value for NumberField but got a string that cannot be converted: {value}"
                )
                raise ValueError(
                    f"Expected a number value for NumberField but got a string that cannot be converted: {value}"
                )

        if not isinstance(value, (int, float)):
            self.logger.error(
                f"Expected a number value for NumberField but got {type(value)}"
            )
            raise ValueError(
                f"Expected a number value for NumberField but got {type(value)}"
            )

        # If the number has more decimal places than allowed, raise an error
        if (
            isinstance(value, float)
            and len(str(value).split(".")[-1]) > self.number_decimal_places
        ):
            self.logger.error(
                f"Value for NumberField exceeds allowed decimal places of {self.number_decimal_places}"
            )
            raise ValueError(
                f"Value for NumberField exceeds allowed decimal places of {self.number_decimal_places}"
            )

        # If negative numbers are not allowed and value is negative, raise an error
        if not self.number_negative and value < 0:
            self.logger.error("Negative values are not allowed for this NumberField")
            raise ValueError("Negative values are not allowed for this NumberField")
