from typing import Any, Dict, List
import logging
from baserowapi.models.fields.field import Field


class RatingField(Field):
    """
    Represents a rating field in Baserow.

    :ivar TYPE: The type of the field, which is 'rating'.
    :vartype TYPE: str
    """

    TYPE = "rating"
    _COMPATIBLE_FILTERS = ["equal", "not_equal", "higher_than", "lower_than"]

    def __init__(self, name: str, field_data: Dict[str, Any], client=None) -> None:
        """
        Initialize a RatingField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        :param client: The Baserow API client. Defaults to None.
        :type client: Optional[Any]
        """
        super().__init__(name, field_data, client)
        self.logger = logging.getLogger(__name__)

        # Extract max_value, color, and style attributes
        self.max_value = field_data.get("max_value")
        if not isinstance(self.max_value, int):
            self.logger.error(
                f"Expected an integer for max_value but got {type(self.max_value)}"
            )
            raise ValueError(
                f"Expected an integer for max_value but got {type(self.max_value)}"
            )

        self.color = field_data.get(
            "color", "dark-orange"
        )  # Defaulting to 'dark-orange' if not provided
        if not isinstance(self.color, str):
            self.logger.error(f"Expected a string for color but got {type(self.color)}")
            raise ValueError(f"Expected a string for color but got {type(self.color)}")

        self.style = field_data.get(
            "style", "star"
        )  # Defaulting to 'star' if not provided
        if not isinstance(self.style, str):
            self.logger.error(f"Expected a string for style but got {type(self.style)}")
            raise ValueError(f"Expected a string for style but got {type(self.style)}")

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this RatingField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS

    def validate_value(self, value: int) -> None:
        """
        Validate the value for a RatingField.

        :param value: The rating value to be validated.
        :type value: int
        :raises ValueError: If the value doesn't match the expected type or constraints.
        """
        if not isinstance(value, int):
            self.logger.error(
                f"Expected an integer value for RatingField but got {type(value)}"
            )
            raise ValueError(
                f"Expected an integer value for RatingField but got {type(value)}"
            )
        if value < 0 or value > self.max_value:
            self.logger.error(
                f"Rating value should be between 0 and {self.max_value}, but got {value}"
            )
            raise ValueError(
                f"Rating value should be between 0 and {self.max_value}, but got {value}"
            )
