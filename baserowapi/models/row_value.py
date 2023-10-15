from typing import Optional, Union, List, Any
import logging
from baserowapi.models.field import *
from datetime import datetime
import os
import requests


class RowValue:
    """
    Represents a value in a Baserow row associated with a specific field.

    Attributes:
        field (:class:`Field`): The associated Field object.
        _raw_value (Optional[Any]): The raw value as returned/fetched from the API.
        logger (logging.Logger): Logger instance for the class.
    """

    def __init__(
        self,
        field: "Field",
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize a RowValue object.

        :param field: The associated Field object.
        :param raw_value: The raw value as returned/fetched from the API.
        :param client: The Baserow class API client. Some child classes of RowValue need access to the API.
        :raises ValueError: If the provided field is not an instance of the Field class.
        """
        if not isinstance(field, Field):
            raise ValueError(
                "The provided field is not an instance of the Field class."
            )

        self.field = field
        self._raw_value = raw_value
        self.client = client
        self.logger = logging.getLogger(__name__)
        self.logger.debug(
            f"Initialized RowValue with field {self.field.name} and value {self._raw_value}"
        )

    def __repr__(self) -> str:
        """
        Provide a string representation of the RowValue object.

        :return: String representation of the Row value.
        :rtype: str
        """
        return f"Baserow row value '{self.name}' of type '{self.type}' with value '{self.value}'"

    @property
    def value(self) -> Any:
        """
        Get the value in a user-friendly format.
        By default, this returns the raw value, but child classes can override this
        for type-specific formatting or conversion.

        :return: User-friendly formatted value.
        """
        return self._raw_value

    @value.setter
    def value(self, new_value: Any) -> None:
        """
        Set a new value.
        This should handle validation and potentially conversion to a format suitable for the API.

        :param new_value: New value to set.
        :raises Exception: If the validation of the new value fails.
        """
        try:
            self.field.validate_value(new_value)
            self._raw_value = (
                new_value  # Child classes can transform this value before setting
            )
            self.logger.debug(f"Set new value {new_value} for field {self.field.name}")
        except Exception as e:
            self.logger.error(
                f"Failed to set value for field {self.field.name}. Error: {e}"
            )
            raise

    def format_for_api(self) -> Any:
        """
        Format the value for API submission.
        By default, returns the value as-is, but child classes can override for type-specific formatting.

        :return: Formatted value for API submission.
        """
        return self._raw_value

    @property
    def is_read_only(self) -> bool:
        """
        Check if the associated field is read-only.

        :return: True if the field is read-only, False otherwise.
        """
        return self.field.is_read_only

    @property
    def type(self) -> str:
        """
        Get the type of the associated field.

        :return: Type of the field.
        """
        return self.field.type

    @property
    def name(self) -> str:
        """
        Get the name of the associated field.

        :return: Name of the field.
        """
        return self.field.name


class TextRowValue(RowValue):
    """
    Represents a RowValue specifically for a TextField.

    Attributes:
        field (:class:`TextField`): The associated TextField object.
        raw_value (Optional[Any]): The raw value as returned/fetched from the API.
        client (Optional[Any]): The Baserow class API client. Some RowValue subclasses may need access to the API.
    """

    def __init__(
        self,
        field: "TextField",
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize a TextRowValue object.

        :param field: The associated TextField object.
        :param raw_value: The raw value as returned/fetched from the API. Default is None.
        :param client: The Baserow class API client. Some RowValue subclasses may need access to the API. Default is None.
        :raises ValueError: If the provided field is not an instance of the TextField class.
        """
        if not isinstance(field, TextField):
            raise ValueError(
                "The provided field is not an instance of the TextField class."
            )

        super().__init__(field, raw_value, client)
        self.logger.debug(
            f"Initialized TextRowValue with field {self.field.name} and value {self._raw_value}"
        )


class LongTextRowValue(RowValue):
    """
    Represents a RowValue specifically for a LongTextField.

    Attributes:
        field (:class:`LongTextField`): The associated LongTextField object.
        raw_value (Optional[Any]): The raw value as returned/fetched from the API.
        client (Optional[Any]): The Baserow class API client. Some RowValue subclasses may need access to the API.
    """

    def __init__(
        self,
        field: "LongTextField",
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize a LongTextRowValue object.

        :param field: The associated LongTextField object.
        :param raw_value: The raw value as returned/fetched from the API. Default is None.
        :param client: The Baserow class API client. Some RowValue subclasses may need access to the API. Default is None.
        :raises ValueError: If the provided field is not an instance of the LongTextField class.
        """
        if not isinstance(field, LongTextField):
            raise ValueError(
                "The provided field is not an instance of the LongTextField class."
            )

        super().__init__(field, raw_value, client)
        self.logger.debug(
            f"Initialized LongTextRowValue with field {self.field.name} and value {self._raw_value}"
        )


class UrlRowValue(RowValue):
    """
    Represents a RowValue specifically for a UrlField.

    Attributes:
        field (:class:`UrlField`): The associated UrlField object.
        raw_value (Optional[Any]): The raw value as returned/fetched from the API.
        client (Optional[Any]): The Baserow class API client. Some RowValue subclasses may need access to the API.
    """

    def __init__(
        self,
        field: "UrlField",
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize a UrlRowValue object.

        :param field: The associated UrlField object.
        :param raw_value: The raw value as returned/fetched from the API. Default is None.
        :param client: The Baserow class API client. Some RowValue subclasses may need access to the API. Default is None.
        :raises ValueError: If the provided field is not an instance of the UrlField class.
        """
        if not isinstance(field, UrlField):
            raise ValueError(
                "The provided field is not an instance of the UrlField class."
            )

        super().__init__(field, raw_value, client)
        self.logger.debug(
            f"Initialized UrlRowValue with field {self.field.name} and value {self._raw_value}"
        )


class EmailRowValue(RowValue):
    """
    Represents a RowValue specifically designed for an EmailField.

    Attributes:
        field (:class:`EmailField`): The associated EmailField object.
        raw_value (Optional[Any]): The raw value as fetched/returned from the API.
        client (Optional[Any]): The Baserow class API client. Some RowValue subclasses may require access to the API.
    """

    def __init__(
        self,
        field: "EmailField",
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize an EmailRowValue object.

        :param field: The associated EmailField object.
        :param raw_value: The raw value as fetched/returned from the API. Default is None.
        :param client: The Baserow class API client. Some RowValue subclasses may require access to the API. Default is None.
        :raises ValueError: If the provided field is not an instance of the EmailField class.
        """
        if not isinstance(field, EmailField):
            raise ValueError(
                "The provided field is not an instance of the EmailField class."
            )

        super().__init__(field, raw_value, client)
        self.logger.debug(
            f"Initialized EmailRowValue with field {self.field.name} and value {self._raw_value}"
        )


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
        :raises ValueError: If the provided field is not an instance of the PhoneNumberField class.
        """
        if not isinstance(field, PhoneNumberField):
            raise ValueError(
                "The provided field is not an instance of the PhoneNumberField class."
            )

        super().__init__(field, raw_value, client)
        self.logger.debug(
            f"Initialized PhoneNumberRowValue with field {self.field.name} and value {self._raw_value}"
        )


class NumberRowValue(RowValue):
    """
    Represents a RowValue specifically designed for a NumberField.

    Attributes:
        field (:class:`NumberField`): The associated NumberField object.
        raw_value (Optional[Union[int, float]]): The raw numeric value as fetched/returned from the API.
        client (Optional[Any]): The Baserow class API client. Some RowValue subclasses may require access to the API.
    """

    def __init__(
        self,
        field: "NumberField",
        raw_value: Optional[Union[int, float]] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize a NumberRowValue object.

        :param field: The associated NumberField object.
        :param raw_value: The raw numeric value as fetched/returned from the API. Default is None.
        :param client: The Baserow class API client. Some RowValue subclasses may require access to the API. Default is None.
        :raises ValueError: If the provided field is not an instance of the NumberField class.
        """
        if not isinstance(field, NumberField):
            raise ValueError(
                "The provided field is not an instance of the NumberField class."
            )

        super().__init__(field, raw_value, client)
        self.logger = logging.getLogger(__name__)
        self.logger.debug(
            f"Initialized NumberRowValue with field {self.field.name} and value {self._raw_value}"
        )

    @property
    def value(self) -> Union[int, float, str]:
        """
        Get the value in a user-friendly format.
        For NumberRowValue, this returns the raw value as a formatted string based on decimal places.

        :return: Formatted value based on the decimal places or the raw value.
        """
        if isinstance(self._raw_value, float):
            format_str = f"{{:.{self.field.decimal_places}f}}"
            return format_str.format(self._raw_value)
        return self._raw_value

    @value.setter
    def value(self, new_value: Union[int, float]) -> None:
        """
        Set a new value.
        This should handle validation specific to NumberRowValue using the associated NumberField's validate_value method.

        :param new_value: The new numeric value to set.
        :raises Exception: If the value is not valid as per the associated NumberField's validation.
        """
        try:
            # Use the validate_value method of the corresponding NumberField class
            self.field.validate_value(new_value)

            self._raw_value = new_value
            self.logger.debug(f"Set new value {new_value} for field {self.field.name}")
        except Exception as e:
            self.logger.error(
                f"Failed to set value for field {self.field.name}. Error: {e}"
            )
            raise


class BooleanRowValue(RowValue):
    """
    Represents a RowValue specifically designed for a BooleanField.

    Attributes:
        field (:class:`BooleanField`): The associated BooleanField object.
        raw_value (Optional[bool]): The raw boolean value as fetched/returned from the API.
        client (Optional[Any]): The Baserow class API client. Some RowValue subclasses may require access to the API.
    """

    def __init__(
        self,
        field: "BooleanField",
        raw_value: Optional[bool] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize a BooleanRowValue object.

        :param field: The associated BooleanField object.
        :param raw_value: The raw boolean value as fetched/returned from the API. Default is None.
        :param client: The Baserow class API client. Some RowValue subclasses may require access to the API. Default is None.
        :raises ValueError: If the provided field is not an instance of the BooleanField class.
        """
        if not isinstance(field, BooleanField):
            raise ValueError(
                "The provided field is not an instance of the BooleanField class."
            )

        super().__init__(field, raw_value, client)
        self.logger.debug(
            f"Initialized BooleanRowValue with field {self.field.name} and value {self._raw_value}"
        )

    @property
    def value(self) -> bool:
        """
        Get the value in a user-friendly format.
        For BooleanRowValue, this returns the raw value as a boolean.

        :return: The boolean value of the raw_value.
        """
        return bool(self._raw_value)

    @value.setter
    def value(self, new_value: bool) -> None:
        """
        Set a new value.
        This should handle validation specific to BooleanRowValue using the associated BooleanField's validate_value method.

        :param new_value: The new boolean value to set.
        :raises Exception: If the value is not valid as per the associated BooleanField's validation.
        """
        try:
            # Use the validate_value method of the corresponding BooleanField class
            self.field.validate_value(new_value)

            self._raw_value = new_value
            self.logger.debug(f"Set new value {new_value} for field {self.field.name}")
        except Exception as e:
            self.logger.error(
                f"Failed to set value for field {self.field.name}. Error: {e}"
            )
            raise


class RatingRowValue(RowValue):
    """
    Represents a RowValue specifically designed for a RatingField.

    Attributes:
        field (:class:`RatingField`): The associated RatingField object.
        raw_value (Optional[Union[int, float]]): The raw numerical value as fetched/returned from the API.
        client (Optional[Any]): The Baserow class API client. Some RowValue subclasses may require access to the API.
    """

    def __init__(
        self,
        field: "RatingField",
        raw_value: Optional[Union[int, float]] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize a RatingRowValue object.

        :param field: The associated RatingField object.
        :param raw_value: The raw numerical value as fetched/returned from the API. Default is None.
        :param client: The Baserow class API client. Some RowValue subclasses may require access to the API. Default is None.
        :raises ValueError: If the provided field is not an instance of the RatingField class.
        """
        if not isinstance(field, RatingField):
            raise ValueError(
                "The provided field is not an instance of the RatingField class."
            )

        super().__init__(field, raw_value, client)
        self.logger.debug(
            f"Initialized RatingRowValue with field {self.field.name} and value {self._raw_value}"
        )

    @property
    def value(self) -> Union[int, float]:
        """
        Get the value in a user-friendly format.
        For RatingRowValue, this returns the raw value directly as it's already user-friendly.

        :return: The numerical value.
        """
        return self._raw_value

    @value.setter
    def value(self, new_value: Union[int, float]) -> None:
        """
        Set a new value.
        This should handle validation specific to RatingRowValue using the associated RatingField's validate_value method.

        :param new_value: The new numerical value to set.
        :raises Exception: If the value is not valid as per the associated RatingField's validation.
        """
        try:
            # Use the validate_value method of the corresponding RatingField class
            self.field.validate_value(new_value)

            self._raw_value = new_value
            self.logger.debug(f"Set new value {new_value} for field {self.field.name}")
        except Exception as e:
            self.logger.error(
                f"Failed to set value for field {self.field.name}. Error: {e}"
            )
            raise


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
        :raises ValueError: If the provided field is not an instance of the BaseDateField class.
        """
        if not isinstance(field, BaseDateField):
            raise ValueError(
                "The provided field is not an instance of the BaseDateField class."
            )

        super().__init__(field, raw_value, client)
        self.logger.debug(
            f"Initialized BaseDateRowValue with field {self.field.name} and value {self._raw_value}"
        )

    @property
    def value(self) -> str:
        """
        Get the value in ISO format.

        :return: The value in ISO format.
        """
        return self._raw_value

    def as_datetime(self) -> datetime:
        """
        Convert and return the value as a Python datetime object.

        :return: The value as a datetime object.
        :raises Exception: If the conversion from ISO format to datetime fails.
        """
        try:
            # If the string ends with 'Z', it's indicating UTC timezone.
            if self._raw_value.endswith("Z"):
                return datetime.fromisoformat(self._raw_value.replace("Z", "+00:00"))
            else:
                return datetime.fromisoformat(self._raw_value)
        except Exception as e:
            self.logger.error(
                f"Failed to convert value to datetime for field {self.field.name}. Error: {e}"
            )
            raise

    @value.setter
    def value(self, new_value: Union[datetime, str]) -> None:
        """
        Set a new value.
        If the new value is a datetime object, it will be converted to ISO format.
        This method also validates the new value using the associated BaseDateField's validate_value method.

        :param new_value: The new value to set, either as a datetime object or in ISO format.
        :raises Exception: If the value is not valid as per the associated BaseDateField's validation.
        """
        try:
            # Check if the new_value is a datetime object, and if so, convert it to ISO format
            if isinstance(new_value, datetime):
                new_value = new_value.isoformat() + "Z"

            # Use the validate_value method of the corresponding BaseDateField class
            self.field.validate_value(new_value)

            self._raw_value = new_value
            self.logger.debug(f"Set new value {new_value} for field {self.field.name}")
        except Exception as e:
            self.logger.error(
                f"Failed to set value for field {self.field.name}. Error: {e}"
            )
            raise

    @property
    def formatted_date(self) -> str:
        """
        Convert the field's value to a formatted string based on the field's settings.

        The method formats the date and time based on field settings such as `date_format`,
        `date_time_format`, and `date_show_tzinfo`.

        :return: The formatted representation of the date or datetime.
        :rtype: str
        :raises ValueError: If the value doesn't match the expected format.
        """
        if self.value is None:
            return None

        # Define format patterns
        date_str_formats = {"US": "%m-%d-%Y", "EU": "%d-%m-%Y", "ISO": "%Y-%m-%d"}
        time_str_formats = {"12": "%I:%M:%S %p", "24": "%H:%M:%S"}

        # Determine the timezone
        try:
            tzinfo = datetime.now().astimezone().tzinfo
        except Exception as e:
            self.logger.error(f"Failed to determine the timezone. Error: {e}")
            raise ValueError(f"Failed to determine the timezone. Error: {e}")

        # Format the date and time based on settings
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
            raise


class DateRowValue(BaseDateRowValue):
    """
    Represents a RowValue specifically designed for a DateField.

    Attributes:
        field (:class:`DateField`): The associated DateField object.
        raw_value (Optional[str]): The raw date value as fetched/returned from the API, typically in ISO format.
        client (Optional[Any]): The Baserow class API client. Some RowValue subclasses may require access to the API.
    """

    def __init__(
        self,
        field: "DateField",
        raw_value: Optional[str] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize a DateRowValue object.

        :param field: The associated DateField object.
        :param raw_value: The raw date value as fetched/returned from the API, typically in ISO format. Default is None.
        :param client: The Baserow class API client. Some RowValue subclasses may require access to the API. Default is None.
        :raises ValueError: If the provided field is not an instance of the DateField class.
        """
        if not isinstance(field, DateField):
            raise ValueError(
                "The provided field is not an instance of the DateField class."
            )

        super().__init__(field, raw_value, client)


class LastModifiedRowValue(BaseDateRowValue):
    """
    Represents a RowValue specifically designed for a LastModifiedField.

    Attributes:
        field (:class:`LastModifiedField`): The associated LastModifiedField object.
        raw_value (Optional[str]): The raw date value as fetched/returned from the API, typically in ISO format.
        client (Optional[Any]): The Baserow class API client. Some RowValue subclasses may require access to the API.
    """

    def __init__(
        self,
        field: "LastModifiedField",
        raw_value: Optional[str] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize a LastModifiedRowValue object.

        :param field: The associated LastModifiedField object.
        :param raw_value: The raw date value as fetched/returned from the API, typically in ISO format. Default is None.
        :param client: The Baserow class API client. Some RowValue subclasses may require access to the API. Default is None.
        :raises ValueError: If the provided field is not an instance of the LastModifiedField class.
        """
        if not isinstance(field, LastModifiedField):
            raise ValueError(
                "The provided field is not an instance of the LastModifiedField class."
            )

        super().__init__(field, raw_value, client)

    @BaseDateRowValue.value.setter
    def value(self, new_value: str) -> None:
        """
        Set a new value for LastModifiedRowValue.
        As LastModifiedRowValue is read-only, it will raise an error if there's an attempt to set a value.

        :param new_value: The new value to be set.
        :raises ValueError: If there's an attempt to set a value for a read-only field.
        """
        msg = "Cannot set value for a read-only LastModifiedRowValue."
        self.logger.error(msg)
        raise ValueError(msg)


class CreatedOnRowValue(BaseDateRowValue):
    """
    Represents a RowValue specifically designed for a CreatedOnField.

    Attributes:
        field (:class:`CreatedOnField`): The associated CreatedOnField object.
        raw_value (Optional[str]): The raw date value as fetched/returned from the API, typically in ISO format.
        client (Optional[Any]): The Baserow class API client. Some RowValue subclasses may require access to the API.
    """

    def __init__(
        self,
        field: "CreatedOnField",
        raw_value: Optional[str] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize a CreatedOnRowValue object.

        :param field: The associated CreatedOnField object.
        :param raw_value: The raw date value as fetched/returned from the API, typically in ISO format. Default is None.
        :param client: The Baserow class API client. Some RowValue subclasses may require access to the API. Default is None.
        :raises ValueError: If the provided field is not an instance of the CreatedOnField class.
        """
        if not isinstance(field, CreatedOnField):
            raise ValueError(
                "The provided field is not an instance of the CreatedOnField class."
            )

        super().__init__(field, raw_value, client)

    @BaseDateRowValue.value.setter
    def value(self, new_value: str) -> None:
        """
        Set a new value for CreatedOnRowValue.
        As CreatedOnRowValue is read-only, it will raise an error if there's an attempt to set a value.

        :param new_value: The new value to be set.
        :raises ValueError: If there's an attempt to set a value for a read-only field.
        """
        msg = "Cannot set value for a read-only CreatedOnRowValue."
        self.logger.error(msg)
        raise ValueError(msg)


class SingleSelectRowValue(RowValue):
    """
    Represents a RowValue specifically designed for a SingleSelectField.

    Attributes:
        field (SingleSelectField): The associated SingleSelectField object.
        raw_value (dict): The raw value as fetched/returned from the API.
        client (Optional[Any]): The Baserow class API client. Some RowValue subclasses may require access to the API.
    """

    def __init__(
        self,
        field: "SingleSelectField",
        raw_value: Optional[dict] = None,
        client: Optional[Any] = None,
    ) -> None:
        """
        Initialize a SingleSelectRowValue object.

        :param field: The associated SingleSelectField object.
        :param raw_value: The raw value as fetched/returned from the API. Default is None.
        :param client: The Baserow class API client. Some RowValue subclasses may require access to the API. Default is None.
        :raises ValueError: If the provided field is not an instance of the SingleSelectField class.
        """
        self._raw_value = raw_value

        if not isinstance(field, SingleSelectField):
            msg = (
                "The provided field is not an instance of the SingleSelectField class."
            )
            self.logger.error(msg)
            raise ValueError(msg)

        super().__init__(field, raw_value, client)
        self.logger.debug(
            f"Initialized SingleSelectRowValue with field {self.field.name} and value {self._raw_value}"
        )

    @property
    def options(self) -> List[str]:
        """
        Get a list of available option values for the associated SingleSelectField.

        This property fetches the "options" attribute from the associated field

        :return: A list of available option values.
        :rtype: List[str]
        :raises AttributeError: If the associated field does not have the "options" attribute.
        """
        try:
            return self.field.options
        except AttributeError:
            msg = f"The associated field {self.field.name} does not have the 'options' attribute."
            self.logger.error(msg)
            raise AttributeError(msg)

    @property
    def value(self) -> str:
        """
        Get the value in a user-friendly format.
        For SingleSelectRowValue, this returns the option's text or "None" if no option is selected.

        :return: The selected option's text or "None" if no option is selected.
        """
        if self._raw_value is None:
            return None
        else:
            return self._raw_value.get("value", "None")

    @value.setter
    def value(self, new_value: Union[int, str]) -> None:
        """
        Set a new value.
        This should handle validation specific to SingleSelectRowValue using the associated SingleSelectField's validate_value method.

        :param new_value: The new value to be set, which can be either an ID or a string corresponding to an option value.
        :raises ValueError: If the provided value doesn't match any select option by ID or value.
        """
        option_details = self.field.options_details

        # Determine the criteria based on the type of new_value
        criteria = (
            "id"
            if isinstance(new_value, int)
            else "value"
            if isinstance(new_value, str)
            else None
        )

        if not criteria:
            msg = f"Invalid input type for value. Expected int or str, got {type(new_value).__name__}."
            self.logger.error(msg)
            raise ValueError(msg)

        matching_option = next(
            (option for option in option_details if option[criteria] == new_value), None
        )

        if not matching_option:
            msg = f"The provided {criteria} '{new_value}' doesn't match any select option."
            self.logger.error(msg)
            raise ValueError(msg)

        self._raw_value = {
            "id": matching_option["id"],
            "value": matching_option["value"],
        }

    def format_for_api(self) -> Optional[int]:
        """
        Format the value for API submission.
        This method will extract the 'id' of the option from the raw_value for API submission.

        :return: The option's id suitable for API submission or None if raw_value is None.
        :raises ValueError: If there's an error in formatting the value for API submission.
        """
        try:
            # Extracting the 'id' from the raw_value for API submission
            if self._raw_value is None:
                return None
            else:
                return self._raw_value["id"]
        except Exception as e:
            msg = f"Failed to format value for API submission for field {self.field.name}. Error: {e}"
            self.logger.error(msg)
            raise ValueError(msg)


class MultipleSelectRowValue(RowValue):
    """
    Represents a RowValue designed for a MultipleSelectField.

    :param field: The associated MultipleSelectField object.
    :type field: MultipleSelectField
    :param raw_value: The raw values as fetched/returned from the API. Defaults to None.
    :type raw_value: List[Optional[Any]], optional
    :param client: The Baserow class API client. Some RowValue subclasses might need this. Defaults to None.
    :type client: Optional[Any], optional
    :raises ValueError: If the provided field is not an instance of the MultipleSelectField class.

    :ivar MultipleSelectField field: The associated MultipleSelectField object.
    :ivar List[Optional[Any]] raw_value: The raw values as fetched/returned from the API.
    :ivar Optional[Any] client: The Baserow class API client.
    """

    def __init__(
        self,
        field: "MultipleSelectField",
        raw_value: List[Optional[Any]] = None,
        client: Optional[Any] = None,
    ):
        self._raw_value = raw_value if raw_value is not None else []

        if not isinstance(field, MultipleSelectField):
            raise ValueError(
                "The provided field is not an instance of the MultipleSelectField class."
            )

        super().__init__(field, raw_value, client)
        self.logger.debug(
            f"Initialized MultipleSelectRowValue with field {self.field.name} and value {self._raw_value}"
        )

    @property
    def options(self) -> List[str]:
        """
        Get a list of available option values for the associated SingleSelectField.

        This property fetches the "options" attribute from the associated field

        :return: A list of available option values.
        :rtype: List[str]
        :raises AttributeError: If the associated field does not have the "options" attribute.
        """
        try:
            return self.field.options
        except AttributeError:
            msg = f"The associated field {self.field.name} does not have the 'options' attribute."
            self.logger.error(msg)
            raise AttributeError(msg)

    @property
    def value(self) -> List[str]:
        """
        Get the values in a user-friendly format. This method returns a list of option names.

        :return: A list of the selected option names.
        :rtype: List[str]
        """
        options = self._raw_value
        return [option["value"] for option in options if option]

    @value.setter
    def value(self, new_values: Union[List[int], List[str]]) -> None:
        """
        Set new values. This method handles validation specific to MultipleSelectRowValue.

        :param new_values: The new values to be set.
        :type new_values: Union[List[int], List[str]]
        :raises ValueError: If one of the values doesn't match any select option or other errors occur.
        """
        if not isinstance(new_values, list):
            raise ValueError("The provided values should be a list.")

        option_dicts = []

        for new_value in new_values:
            if isinstance(new_value, int) or isinstance(new_value, str):
                option = self.field._get_option_by_id_or_value(new_value)
                if option:
                    option_dicts.append(option)
                else:
                    raise ValueError(
                        f"The value '{new_value}' doesn't match any select option."
                    )
            else:
                raise ValueError(
                    f"Invalid type '{type(new_value).__name__}' for value. Expected int or str."
                )

        self._raw_value = option_dicts

    def format_for_api(self) -> List[int]:
        """
        Format the values suitable for API submission.

        :return: The formatted values suitable for API submission.
        :rtype: List[int]
        :raises ValueError: If there's an error in formatting the values.
        """
        try:
            # Extracting the 'id' from each option dictionary in the raw_value for API submission
            return [option["id"] for option in self._raw_value]
        except Exception as e:
            raise ValueError(
                f"Failed to format values for API submission for field {self.field.name}. Error: {e}"
            )


class FormulaRowValue(RowValue):
    """
    Represents a RowValue designed for a FormulaField.

    :param field: The associated FormulaField object.
    :type field: FormulaField
    :param raw_value: The raw value as fetched/returned from the API. Defaults to None.
    :type raw_value: Optional[Any], optional
    :param client: The Baserow class API client. Some RowValue subclasses might need this. Defaults to None.
    :type client: Optional[Any], optional
    :raises ValueError: If the provided field is not an instance of the FormulaField class.

    :ivar FormulaField field: The associated FormulaField object.
    :ivar Optional[Any] raw_value: The raw value as fetched/returned from the API.
    :ivar Optional[Any] client: The Baserow class API client.
    """

    def __init__(
        self,
        field: "FormulaField",
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ):
        if not isinstance(field, FormulaField):
            raise ValueError(
                "The provided field is not an instance of the FormulaField class."
            )

        super().__init__(field, raw_value, client)

    @property
    def value(self) -> Any:
        """
        Get the value in a user-friendly format. This method returns the raw value.

        :return: The raw value of the FormulaRowValue.
        :rtype: Any
        """
        return self._raw_value

    @value.setter
    def value(self, new_value: Any):
        """
        Set a new value. As FormulaRowValue is read-only, this method raises an error.

        :param new_value: The new value to be set.
        :type new_value: Any
        :raises ValueError: As the FormulaRowValue is read-only, setting a value will always raise this error.
        """
        raise ValueError("Cannot set value for a read-only FormulaRowValue.")

    def format_for_api(self) -> Any:
        """
        Format the value suitable for API submission. This method returns the raw value.

        :return: The raw value suitable for API submission.
        :rtype: Any
        """
        return self._raw_value


class TableLinkRowValue(RowValue):
    """
    Represents a RowValue designed for a TableLinkField.

    :param field: The associated TableLinkField object.
    :type field: TableLinkField
    :param raw_value: The raw value as fetched/returned from the API. Defaults to None.
    :type raw_value: Optional[List[Union[int, str]]], optional
    :param client: The Baserow class API client. Some RowValue subclasses might need this. Defaults to None.
    :type client: Optional[Any], optional
    :raises ValueError: If the provided field is not an instance of the TableLinkField class.

    :ivar TableLinkField field: The associated TableLinkField object.
    :ivar Optional[List[Union[int, str]]] raw_value: The raw value as fetched/returned from the API.
    :ivar Optional[Any] client: The Baserow class API client.
    """

    def __init__(
        self,
        field: "TableLinkField",
        raw_value: Optional[List[Union[int, str]]] = None,
        client: Optional[Any] = None,
    ):
        if not isinstance(field, TableLinkField):
            raise ValueError(
                "The provided field is not an instance of the TableLinkField class."
            )

        super().__init__(field, raw_value, client)

    @property
    def value(self) -> List[Union[int, str]]:
        """
        Get the value in a user-friendly format. This method returns a list of primary field values or IDs.

        :return: A list of primary field values or IDs.
        :rtype: List[Union[int, str]]
        """
        return [entry.get("value", entry.get("id", "")) for entry in self._raw_value]

    @value.setter
    def value(self, new_value: List[Union[int, str]]):
        """
        Set a new value for TableLinkRowValue. Accepts either primary field values or row IDs from the linked table.

        :param new_value: The new values to be set.
        :type new_value: List[Union[int, str]]
        :raises ValueError: If the provided values are not in the expected format or there are mixed types of IDs and values.
        """
        if not isinstance(new_value, list):
            raise ValueError(
                "The provided value for TableLinkRowValue should be a list."
            )

        if all(isinstance(val, int) for val in new_value):
            self._raw_value = [{"id": val, "value": val} for val in new_value]
        elif all(isinstance(val, str) for val in new_value):
            self._raw_value = [{"value": val} for val in new_value]
        else:
            raise ValueError(
                "Mixed types of IDs and values provided for TableLinkRowValue."
            )

    def format_for_api(self) -> List[Union[int, str]]:
        """
        Format the value suitable for API submission. This method returns a list of IDs if they exist or values otherwise.

        :return: A list of IDs or values suitable for API submission.
        :rtype: List[Union[int, str]]
        """
        return [entry.get("id", entry.get("value")) for entry in self._raw_value]

    def get_related_table(self):
        """
        Fetches and returns the related table associated with the `TableLinkRowValue`.

        This method utilizes the `link_row_table_id` attribute from the associated `TableLinkField`
        to fetch the table data from the Baserow API.

        :return: The related table object.
        :rtype: Table (or whatever the type returned by client.get_table() is)
        :raises ValueError: If there's an error fetching the related table.
        """
        try:
            # Fetch the related table using the client's get_table method
            related_table = self.client.get_table(self.field.link_row_table_id)

            # Logging the successful fetch operation
            self.logger.debug(
                f"Fetched related table with ID {self.field.link_row_table_id} for TableLinkRowValue associated with field {self.field.name}"
            )

            return related_table
        except Exception as e:
            # Logging the error
            self.logger.error(
                f"Failed to fetch related table with ID {self.field.link_row_table_id} for TableLinkRowValue associated with field {self.field.name}. Error: {e}"
            )

            # Raising an error for external handling or informing the caller
            raise ValueError(f"Failed to fetch the related table. Error: {e}")

    def get_options(self) -> List[str]:
        """
        Fetches and returns the primary values from the related table that are possible
        for the TableLinkRowValue.

        This method retrieves the rows from the related table and extracts the primary
        field values from each row.

        :return: A list of primary field values from the related table.
        :raises ValueError: If there's an error fetching the primary values from the related table.
        """
        try:
            related_table = self.get_related_table()
            primary_field_name = related_table.primary_field
            returned_rows = related_table.get_rows(include=[primary_field_name])
            options = [row[primary_field_name] for row in returned_rows]

            self.logger.debug(
                f"Retrieved {len(options)} options for TableLinkRowValue associated with field {self.field.name} from related table {related_table.id}"
            )
            return options
        except Exception as e:
            self.logger.error(
                f"Failed to retrieve options for TableLinkRowValue associated with field {self.field.name}. Error: {e}"
            )
            raise ValueError(
                f"Failed to retrieve options from the related table. Error: {e}"
            )


class CountRowValue(RowValue):
    """
    Represents a RowValue designed for a CountField.

    :param field: The associated CountField object.
    :type field: CountField
    :param raw_value: The raw value as fetched/returned from the API, representing the main (primary) field text values of the linked rows. Defaults to None.
    :type raw_value: Optional[Any], optional
    :param client: The Baserow class API client. Some RowValue subclasses might need this. Defaults to None.
    :type client: Optional[Any], optional
    :raises ValueError: If the provided field is not an instance of the CountField class.

    :ivar CountField field: The associated CountField object.
    :ivar Optional[Any] raw_value: The raw value as fetched/returned from the API.
    :ivar Optional[Any] client: The Baserow class API client.
    """

    def __init__(
        self,
        field: "CountField",
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ):
        super().__init__(field, raw_value, client)

        if not isinstance(field, CountField):
            raise ValueError(
                "The provided field is not an instance of the CountField class."
            )

    @property
    def value(self) -> Any:
        """
        Get the value in a user-friendly format. This method returns the main (primary) field text values of the linked rows.

        :return: The main (primary) field text values of the linked rows.
        :rtype: Any
        """
        return self._raw_value

    @value.setter
    def value(self, new_value: Any):
        """
        Set a new value for CountRowValue. Since CountRowValue is read-only, setting a value will raise an error.

        :param new_value: The new value to be set.
        :type new_value: Any
        :raises ValueError: As the CountRowValue is read-only, setting a value will always raise an error.
        """
        raise ValueError("Cannot set value for a read-only CountRowValue.")

    def format_for_api(self) -> Any:
        """
        Format the value suitable for API submission. This method directly returns the raw value.

        :return: The value formatted for API submission.
        :rtype: Any
        """
        return self._raw_value


class LookupRowValue(RowValue):
    """
    Represents a RowValue designed for a LookupField.

    :param field: The associated LookupField object.
    :type field: LookupField
    :param raw_value: The raw value as fetched/returned from the API, representing an array of values and row IDs. Defaults to None.
    :type raw_value: Optional[Any], optional
    :param client: The Baserow class API client. Some RowValue subclasses might need this. Defaults to None.
    :type client: Optional[Any], optional
    :raises ValueError: If the provided field is not an instance of the LookupField class.

    :ivar LookupField field: The associated LookupField object.
    :ivar Optional[Any] raw_value: The raw value as fetched/returned from the API.
    :ivar Optional[Any] client: The Baserow class API client.
    """

    def __init__(
        self,
        field: "LookupField",
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ):
        super().__init__(field, raw_value, client)

        if not isinstance(field, LookupField):
            raise ValueError(
                "The provided field is not an instance of the LookupField class."
            )

    @property
    def value(self) -> Any:
        """
        Get the value in a user-friendly format. This method returns the raw value (an array of values and row IDs).

        :return: The raw value, which is an array of values and row IDs.
        :rtype: Any
        """
        return self._raw_value

    @value.setter
    def value(self, new_value: Any):
        """
        Set a new value for LookupRowValue. Since LookupRowValue is read-only, setting a value will raise an error.

        :param new_value: The new value to be set.
        :type new_value: Any
        :raises ValueError: As the LookupRowValue is read-only, setting a value will always raise an error.
        """
        raise ValueError("Cannot set value for a read-only LookupRowValue.")

    def format_for_api(self) -> Any:
        """
        Format the value suitable for API submission. This method directly returns the raw value.

        :return: The value formatted for API submission.
        :rtype: Any
        """
        return self._raw_value


class MultipleCollaboratorsRowValue(RowValue):
    """
    Represents a RowValue designed for a MultipleCollaboratorsField.

    :param field: The associated MultipleCollaboratorsField object.
    :type field: MultipleCollaboratorsField
    :param raw_value: The raw value as fetched/returned from the API. Defaults to None.
    :type raw_value: Optional[Any], optional
    :param client: The Baserow class API client. Some RowValue subclasses might need this. Defaults to None.
    :type client: Optional[Any], optional
    :raises ValueError: If the provided field is not an instance of the MultipleCollaboratorsField class.

    :ivar MultipleCollaboratorsField field: The associated MultipleCollaboratorsField object.
    :ivar Optional[Any] raw_value: The raw value as fetched/returned from the API.
    :ivar Optional[Any] client: The Baserow class API client.
    """

    def __init__(
        self,
        field: "MultipleCollaboratorsField",
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ):
        super().__init__(field, raw_value, client)

    @property
    def value(self) -> Any:
        """
        Get the value in a user-friendly format. This method returns the raw value.

        :return: The raw value.
        :rtype: Any
        """
        return self._raw_value

    @value.setter
    def value(self, new_value: Any):
        """
        Validate and set the new value for MultipleCollaboratorsRowValue.

        :param new_value: The new value to be set.
        :type new_value: Any
        """
        self.field.validate_value(new_value)
        self._raw_value = new_value

    def format_for_api(self) -> Any:
        """
        Format the value suitable for API submission. This method formats it in a way that only returns the IDs of the collaborators.

        :return: The value formatted for API submission.
        :rtype: Any
        """
        return self.field.format_for_api(self._raw_value)


class FileRowValue(RowValue):
    """
    Represents a RowValue designed for a FileField.

    :param field: The associated FileField object.
    :type field: FileField
    :param client: The Baserow class API client to make API requests.
    :type client: Any
    :param raw_value: The raw value as fetched/returned from the API. Defaults to None.
    :type raw_value: Optional[List[Any]], optional
    :raises ValueError: If the provided field is not an instance of the FileField class.

    :ivar FileField field: The associated FileField object.
    :ivar Any client: The Baserow class API client to make API requests.
    :ivar Optional[List[Any]] raw_value: The raw value as fetched/returned from the API.
    """

    def __init__(
        self, field: "FileField", client: Any, raw_value: Optional[List[Any]] = None
    ):
        if not isinstance(field, FileField):
            raise ValueError(
                "The provided field is not an instance of the FileField class."
            )

        self.client = client
        super().__init__(field, raw_value, client)

        if self._raw_value is None:
            self._raw_value = []

    def upload_file_to_server(
        self,
        file_path: Optional[str] = None,
        url: Optional[str] = None,
        replace: bool = False,
    ) -> List[Any]:
        """
        Upload a file or files to Baserow either from a local path or by downloading it from a provided URL.
        The method either appends or replaces the current value based on the 'replace' flag.

        Note: This function updates the in-memory representation of the row value.
        Use `row.update()` to save the updated value to the server.

        :param file_path: Path to the file or directory to be uploaded. Defaults to None.
        :type file_path: Optional[str]
        :param url: The URL of the file to download and upload. Defaults to None.
        :type url: Optional[str]
        :param replace: If True, replaces the current value with the uploaded file's data.
                        Otherwise, appends. Defaults to False.
        :type replace: bool
        :return: A list of file object representations returned by Baserow.
        :rtype: List[Any]
        :raises ValueError: If neither file_path nor url is provided.
        :raises Exception: If there's an error during the upload process.
        """

        if not file_path and not url:
            raise ValueError("Either file_path or url must be provided.")

        endpoint_file = "/api/user-files/upload-file/"
        endpoint_url = "/api/user-files/upload-via-url/"
        uploaded_files = []

        # Upload local files
        if file_path:
            if os.path.isdir(file_path):
                files_to_upload = [
                    os.path.join(file_path, file) for file in os.listdir(file_path)
                ]
            else:
                files_to_upload = [file_path]

            for file in files_to_upload:
                try:
                    with open(file, "rb") as f:
                        response = self.client.make_api_request(
                            endpoint_file, method="POST", files={"file": f}
                        )
                        uploaded_files.append(response)
                except Exception as e:
                    error_message = f"Failed to upload file {file}. Error: {e}"
                    self.logger.error(error_message)
                    raise Exception(error_message)

        # Upload file from URL
        if url:
            try:
                data = {"url": url}
                response = self.client.make_api_request(
                    endpoint_url, method="POST", data=data
                )
                uploaded_files.append(response)
            except Exception as e:
                self.logger.error(f"Failed to upload file from URL {url}. Error: {e}")
                raise

        # Update in-memory value based on the 'replace' flag
        if replace:
            self.value = uploaded_files
        else:
            self.value.extend(uploaded_files)

        return uploaded_files

    def download_files(self, directory_path: str) -> List[str]:
        """
        Downloads all file objects in the FileRowValue to the specified directory.

        :param directory_path: The path to the directory where the files should be downloaded.
        :type directory_path: str
        :return: List of filenames that were successfully downloaded.
        :rtype: List[str]
        :raises Exception: If there's an error during the download process.
        """
        logger = logging.getLogger(__name__)
        downloaded_files = (
            []
        )  # List to store the names of successfully downloaded files

        # Ensure the target directory exists
        os.makedirs(directory_path, exist_ok=True)

        for file_obj in self._raw_value:
            file_url = file_obj["url"]
            file_name = file_obj["original_name"]
            target_file_path = os.path.join(directory_path, file_name)

            # Check if the file already exists in the target directory
            if os.path.exists(target_file_path):
                logger.info(
                    f"File {file_name} already exists in {directory_path}. Skipping download."
                )
                continue

            try:
                # Download the file
                response = requests.get(file_url, stream=True)
                response.raise_for_status()

                # Save the downloaded file to the target directory
                with open(target_file_path, "wb") as out_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        out_file.write(chunk)

                logger.debug(
                    f"File {file_name} downloaded successfully to {directory_path}."
                )
                downloaded_files.append(
                    file_name
                )  # Append the file name to the downloaded_files list

            except requests.RequestException as e:
                logger.error(
                    f"Failed to download file {file_name} from {file_url}. Error: {e}"
                )
                raise Exception(f"Failed to download file {file_name}. Error: {e}")

        return downloaded_files  # Return the list of successfully downloaded files


class RowValueList:
    """
    A list-like container for RowValue objects.

    :ivar row_values: A list of RowValue objects.
    :vartype row_values: List[RowValue]
    """

    def __init__(self, row_values: Union[List["RowValue"], None] = None) -> None:
        """
        Initializes a RowValueList instance.

        :param row_values: A list of RowValue objects. Defaults to an empty list if not provided.
        :type row_values: Union[List[RowValue], None], optional
        """
        self.row_values = row_values if row_values else []

    def __repr__(self) -> str:
        """
        Provides a string representation of the RowValueList object.

        :return: A string representation of the RowValueList object.
        :rtype: str
        """
        max_values_to_show = 5
        value_names = [value.field.name for value in self.row_values]

        if len(value_names) > max_values_to_show:
            value_names = value_names[:max_values_to_show] + ["..."]

        values_str = ", ".join(value_names)
        return f"RowValueList({len(self.row_values)} values: [{values_str}])"

    def __getitem__(self, field_name: str) -> "RowValue":
        """
        Retrieve a RowValue object from the list by its field name.

        :param field_name: The name of the field to search for.
        :type field_name: str
        :raises KeyError: If the field name is not found in the list.
        :return: The found RowValue object.
        :rtype: RowValue
        """
        for value in self.row_values:
            if value.field.name == field_name:
                return value
        raise KeyError(f"RowValue with field name '{field_name}' not found.")

    def __iter__(self):
        """
        Allows iteration over the RowValue objects in the list.

        :return: An iterator over the RowValue objects.
        :rtype: Iterator[RowValue]
        """
        return iter(self.row_values)

    def __len__(self) -> int:
        """
        Returns the number of RowValue objects in the list.

        :return: The number of RowValue objects.
        :rtype: int
        """
        return len(self.row_values)

    def add(self, row_value: "RowValue") -> None:
        """
        Add a RowValue object to the list.

        :param row_value: The RowValue object to be added.
        :type row_value: RowValue
        :raises TypeError: If the provided object is not an instance of RowValue.
        """
        if not isinstance(row_value, RowValue):
            raise TypeError(
                "The provided object is not an instance of the RowValue class."
            )

        self.row_values.append(row_value)
