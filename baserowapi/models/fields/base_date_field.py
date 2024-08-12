from typing import Any, Dict, Optional
from datetime import datetime
from baserowapi.models.fields.field import Field
from baserowapi.exceptions import FieldValidationError


class BaseDateField(Field):
    """
    Represents a base date field in Baserow.

    :ivar TYPE: The type of the field, which is 'base_date'.
    :vartype TYPE: str
    """

    TYPE = "base_date"

    def __init__(self, name: str, field_data: Dict[str, Any], client=None) -> None:
        """
        Initialize a BaseDateField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        :param client: The Baserow API client. Defaults to None.
        :type client: Optional[Any]
        """
        super().__init__(name, field_data, client)

        # Common attributes for date fields
        self.date_format: str = field_data.get("date_format", "EU")
        self.date_include_time: bool = field_data.get("date_include_time", True)
        self.date_time_format: str = field_data.get("date_time_format", "24")
        self.date_show_tzinfo: bool = field_data.get("date_show_tzinfo", False)
        self.date_force_timezone: Optional[str] = field_data.get(
            "date_force_timezone", None
        )

        # Validate the extracted attributes
        if self.date_format not in ["US", "EU", "ISO"]:
            self.logger.error(
                f"Invalid date_format: {self.date_format}. Expected one of ['US', 'EU', 'ISO']."
            )
            raise FieldValidationError(
                f"Invalid date_format: {self.date_format}. Expected one of ['US', 'EU', 'ISO']."
            )

        if self.date_time_format not in ["12", "24"]:
            self.logger.error(
                f"Invalid date_time_format: {self.date_time_format}. Expected one of ['12', '24']."
            )
            raise FieldValidationError(
                f"Invalid date_time_format: {self.date_time_format}. Expected one of ['12', '24']."
            )

    def validate_value(self, value: str) -> None:
        """
        Validate the date or datetime value based on the field's attributes.

        :param value: The date or datetime value to be validated.
        :type value: str
        :raises FieldValidationError: If the value doesn't match the expected format.
        """
        # If the value is None, it is considered valid
        if value is None:
            return

        if self.date_include_time:
            # First, try validating with fractional seconds format
            try:
                datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
                return
            except ValueError:
                pass

            # Next, try without fractional seconds but with UTC offset
            try:
                datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z")
                return
            except ValueError:
                pass

            # Finally, try without fractional seconds and with 'Z' as the UTC offset
            try:
                datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
                return
            except ValueError:
                self.logger.error(f"Invalid date format for {self.TYPE}: {value}")
                raise FieldValidationError(
                    f"Invalid date format for {self.TYPE}: {value}"
                )
        else:
            # If only date is expected but value contains time, raise an error
            if "T" in value:
                self.logger.error(
                    f"Time information not allowed for {self.TYPE}: {value}"
                )
                raise FieldValidationError(
                    f"Time information not allowed for {self.TYPE}: {value}"
                )

            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                self.logger.error(f"Invalid date format for {self.TYPE}: {value}")
                raise FieldValidationError(
                    f"Invalid date format for {self.TYPE}: {value}"
                )
