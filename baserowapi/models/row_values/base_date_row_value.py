from typing import Optional, Union, Any
from datetime import datetime
from baserowapi.models.fields.base_date_field import BaseDateField
from baserowapi.models.row_values.row_value import RowValue
from baserowapi.exceptions import InvalidRowValueError, RowValueOperationError


class BaseDateRowValue(RowValue):
    """
    Represents a RowValue specifically designed for a BaseDateField.

    Attributes:
        field (:class:`BaseDateField`): The associated BaseDateField object.
        raw_value (Optional[str]): The raw date value as fetched/returned from the API, typically in ISO format.
        client (Optional[Any]): The Baserow class API client. Some RowValue subclasses may require access to the API.
    """

    def __init__(
        self,
        field: "BaseDateField",
        raw_value: Optional[str] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize a BaseDateRowValue object.

        :param field: The associated BaseDateField object.
        :param raw_value: The raw date value as fetched/returned from the API, typically in ISO format. Default is None.
        :param client: The Baserow class API client. Some RowValue subclasses may require access to the API. Default is None.
        :raises InvalidRowValueError: If the provided field is not an instance of BaseDateField.
        """
        super().__init__(field, raw_value, client)
        if not isinstance(field, BaseDateField):
            raise InvalidRowValueError(
                f"The provided field is not an instance of the BaseDateField class. Received: {type(field).__name__}"
            )
        self.logger.debug(
            f"Initialized BaseDateRowValue with field {self.field.name} and value {self._raw_value}"
        )

    @property
    def value(self) -> Optional[str]:
        """
        Get the value in ISO format.

        :return: The value in ISO format, or None if no value is set.
        """
        return self._raw_value

    def as_datetime(self) -> Optional[datetime]:
        """
        Convert and return the value as a Python datetime object.

        :return: The value as a datetime object, or None if the value is None.
        :raises RowValueOperationError: If the conversion from ISO format to datetime fails.
        """
        if self._raw_value is None:
            return None

        try:
            if self._raw_value.endswith("Z"):
                return datetime.fromisoformat(self._raw_value.replace("Z", "+00:00"))
            else:
                return datetime.fromisoformat(self._raw_value)
        except Exception as e:
            self.logger.error(
                f"Failed to convert value to datetime for field {self.field.name}. Error: {e}"
            )
            raise RowValueOperationError(
                f"Failed to convert value to datetime for field {self.field.name}. Error: {e}"
            )

    @value.setter
    def value(self, new_value: Union[datetime, str, None]) -> None:
        """
        Set a new value.
        If the new value is a datetime object, it will be converted to ISO format.
        This method also validates the new value using the associated BaseDateField's validate_value method.

        :param new_value: The new value to set, either as a datetime object, in ISO format, or None.
        :raises InvalidRowValueError: If the value is not valid as per the associated BaseDateField's validation.
        """
        try:
            if isinstance(new_value, datetime):
                new_value = new_value.isoformat() + "Z"

            self.field.validate_value(new_value)
            self._raw_value = new_value
            self.logger.debug(f"Set new value {new_value} for field {self.field.name}")
        except Exception as e:
            self.logger.error(
                f"Failed to set value for field {self.field.name}. Error: {e}"
            )
            raise InvalidRowValueError(
                f"Failed to set value for field {self.field.name}. Error: {e}"
            )

    @property
    def formatted_date(self) -> Optional[str]:
        """
        Convert the field's value to a formatted string based on the field's settings.

        The method formats the date and time based on field settings such as `date_format`,
        `date_time_format`, and `date_show_tzinfo`.

        :return: The formatted representation of the date or datetime, or None if the value is None.
        :rtype: Optional[str]
        :raises RowValueOperationError: If the value doesn't match the expected format or if timezone determination fails.
        """
        if self.value is None:
            return None

        date_str_formats = {"US": "%m-%d-%Y", "EU": "%d-%m-%Y", "ISO": "%Y-%m-%d"}
        time_str_formats = {"12": "%I:%M:%S %p", "24": "%H:%M:%S"}

        try:
            tzinfo = datetime.now().astimezone().tzinfo
        except Exception as e:
            self.logger.error(f"Failed to determine the timezone. Error: {e}")
            raise RowValueOperationError(
                f"Failed to determine the timezone. Error: {e}"
            )

        try:
            if self.field.date_include_time:
                try:
                    dt_object = datetime.strptime(self.value, "%Y-%m-%dT%H:%M:%S.%fZ")
                except ValueError:
                    dt_object = datetime.strptime(self.value, "%Y-%m-%dT%H:%M:%S%z")

                dt_object = dt_object.astimezone(tzinfo)
                date_str = dt_object.strftime(
                    date_str_formats.get(self.field.date_format, "%Y-%m-%d")
                )
                time_str = dt_object.strftime(
                    time_str_formats.get(self.field.date_time_format, "%H:%M:%S")
                )

                formatted_date = f"{date_str} {time_str}"
                if self.field.date_show_tzinfo:
                    formatted_date += f" {dt_object.tzname()}"

                return formatted_date

            else:
                dt_object = datetime.strptime(self.value, "%Y-%m-%d")
                return dt_object.strftime(
                    date_str_formats.get(self.field.date_format, "%Y-%m-%d")
                )
        except ValueError as e:
            self.logger.error(
                f"Invalid date format for {self.type}: {self.value}. Error: {e}"
            )
            raise RowValueOperationError(
                f"Invalid date format for {self.type}: {self.value}. Error: {e}"
            )
