from typing import Any, Dict, List, Union, Iterator, Union, Optional
import logging
import re
from datetime import datetime


class Field:
    """
    Represents a field in Baserow and provides methods to interact with its properties.
    """

    def __init__(self, name: str, field_data: Dict[str, Any]) -> None:
        """
        Initialize a Field object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's attributes.
        :type field_data: Dict[str, Any]
        :raises ValueError: If the name is empty or if field_data is not a valid dictionary.
        """
        self.logger = logging.getLogger(__name__)

        if not name:
            self.logger.error("Name not provided for Field initialization.")
            raise ValueError("Name should not be empty.")

        if not field_data or not isinstance(field_data, dict):
            self.logger.error("Invalid field data provided for Field initialization.")
            raise ValueError("Field data should be a non-empty dictionary.")

        self.name = name
        self.field_data = field_data
        self.logger.debug(
            f"Initialized field '{self.name}' with attributes '{self.field_data}'"
        )

    def __repr__(self) -> str:
        """
        Provide a string representation of the Field object.

        :return: String representation of the Field.
        :rtype: str
        """
        return f"Baserow field '{self.name}' with id '{self.id}' of type '{self.type}' of table '{self.table_id}'"

    def __getitem__(self, key: str) -> Any:
        """
        Retrieve an attribute from field_data.

        :param key: The attribute's key.
        :type key: str
        :return: The desired attribute.
        :rtype: Any
        :raises KeyError: If the key doesn't exist in field_data.
        """
        try:
            return self.field_data[key]
        except KeyError:
            self.logger.error(f"Attribute '{key}' not found in field '{self.name}'.")
            raise

    def validate_value(self, value: Any) -> None:
        """
        Validate the value against the field's criteria.

        Child classes can override for custom rules.

        :param value: The value to be validated.
        :type value: Any
        """
        pass

    def format_for_api(self, value: Any) -> Any:
        """
        Format the value for API submission.

        Child classes can override for custom formatting.

        :param value: The value to be formatted.
        :type value: Any
        :return: The formatted value.
        :rtype: Any
        """
        return value

    @property
    def id(self) -> Union[int, None]:
        """
        Retrieve the ID of the field.

        :return: The ID of the field or None if not present.
        :rtype: Union[int, None]
        """
        field_id = self.field_data.get("id", None)
        if field_id is None:
            self.logger.warning(f"Field ID missing for field {self.name}.")
        return field_id

    @property
    def table_id(self) -> Union[int, None]:
        """
        Retrieve the table ID associated with the field.

        :return: The table ID or None if not present.
        :rtype: Union[int, None]
        """
        table_id = self.field_data.get("table_id", None)
        if table_id is None:
            self.logger.warning(f"Table ID missing for field {self.name}.")
        return table_id

    @property
    def order(self) -> Union[int, None]:
        """
        Retrieve the order of the field.

        :return: The order of the field or None if not present.
        :rtype: Union[int, None]
        """
        order = self.field_data.get("order", None)
        if order is None:
            self.logger.warning(f"Order missing for field {self.name}.")
        return order

    @property
    def type(self) -> Union[str, None]:
        """
        Retrieve the type of the field.

        :return: The type of the field or None if not present.
        :rtype: Union[str, None]
        """
        field_type = self.field_data.get("type", None)
        if field_type is None:
            self.logger.warning(f"Field type missing for field {self.name}.")
        return field_type

    @property
    def is_primary(self) -> bool:
        """
        Determine if the field is primary.

        :return: True if the field is primary, otherwise False.
        :rtype: bool
        """
        return self.field_data.get("primary", False)

    @property
    def is_read_only(self) -> bool:
        """
        Determine if the field is read-only.

        :return: True if the field is read-only, otherwise False.
        :rtype: bool
        """
        return self.field_data.get("read_only", False)


class BaseTextClass(Field):
    """A base class for text-based fields in Baserow."""

    def validate_value(self, value: Any) -> None:
        """
        Validate the value for a text-based Field.

        :param value: The value to be validated.
        :raises ValueError: If the value is not of type `str`.
        """
        if value is None:
            return
        elif not isinstance(value, str):
            raise ValueError(
                f"Expected a string value for {type(self).__name__} but got {type(value)}"
            )


class TextField(BaseTextClass):
    """
    Represents a text field in Baserow.

    :ivar TYPE: The type of the field, which is 'text'.
    :vartype TYPE: str
    """

    TYPE = "text"

    _COMPATIBLE_FILTERS = [
        "equal",
        "not_equal",
        "contains",
        "contains_not",
        "contains_word",
        "doesnt_contain_word",
        "length_is_lower_than",
        "empty",
        "not_empty",
    ]

    def __init__(self, name: str, field_data: Dict[str, Any]):
        """
        Initialize a TextField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        :raises ValueError: If the 'text_default' value in field_data is not a string.
        """
        super().__init__(name, field_data)

        text_default_value = field_data.get("text_default", "")
        if not isinstance(text_default_value, str):
            self.logger.error(
                f"Expected a string for text_default but got {type(text_default_value)}"
            )
            raise ValueError(
                f"Expected a string for text_default but got {type(text_default_value)}"
            )

        self._text_default = text_default_value

    @property
    def text_default(self) -> str:
        """
        Get the default text value for this TextField.

        :return: The default text value.
        :rtype: str
        """
        return self._text_default

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this TextField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS


class LongTextField(BaseTextClass):
    """
    Represents a long text field in Baserow.

    :ivar TYPE: The type of the field, which is 'long_text'.
    :vartype TYPE: str
    """

    TYPE = "long_text"
    _COMPATIBLE_FILTERS = [
        "equal",
        "not_equal",
        "contains",
        "contains_not",
        "contains_word",
        "doesnt_contain_word",
        "length_is_lower_than",
        "empty",
        "not_empty",
    ]

    def __init__(self, name: str, field_data: Dict[str, Any]):
        """
        Initialize a LongTextField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        """
        super().__init__(name, field_data)

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this LongTextField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS


class UrlField(BaseTextClass):
    """
    Represents a URL field in Baserow.

    :ivar TYPE: The type of the field, which is 'url'.
    :vartype TYPE: str
    """

    TYPE = "url"
    _COMPATIBLE_FILTERS = [
        "equal",
        "not_equal",
        "contains",
        "contains_not",
        "contains_word",
        "doesnt_contain_word",
        "length_is_lower_than",
        "empty",
        "not_empty",
    ]

    def __init__(self, name: str, field_data: Dict[str, Any]):
        """
        Initialize a UrlField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        """
        super().__init__(name, field_data)

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this UrlField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS


class EmailField(BaseTextClass):
    """
    Represents an email field in Baserow.

    :ivar TYPE: The type of the field, which is 'email'.
    :vartype TYPE: str
    """

    TYPE = "email"
    _COMPATIBLE_FILTERS = [
        "equal",
        "not_equal",
        "contains",
        "contains_not",
        "contains_word",
        "doesnt_contain_word",
        "length_is_lower_than",
        "empty",
        "not_empty",
    ]

    def __init__(self, name: str, field_data: Dict[str, Any]):
        """
        Initialize an EmailField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        """
        super().__init__(name, field_data)

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this EmailField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS


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

    def __init__(self, name: str, field_data: Dict[str, Any]):
        """
        Initialize a PhoneNumberField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        """
        super().__init__(name, field_data)
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
        :raises ValueError: If the phone number doesn't match the expected format.
        """
        if value is None:
            return
        if not self.valid_characters.match(value):
            self.logger.error(
                f"The provided phone number '{value}' doesn't match the expected format."
            )
            raise ValueError(
                f"The provided phone number '{value}' doesn't match the expected format."
            )

    def format_for_api(self, value: str) -> str:
        """
        Format the value for API submission.

        For PhoneNumberField, it would return the phone number as-is after validation.

        :param value: The phone number string to be formatted.
        :type value: str
        :return: The formatted phone number.
        :rtype: str
        :raises ValueError: If the phone number doesn't match the expected format.
        """
        self.validate_value(value)  # Validate before formatting
        return value


class BooleanField(Field):
    """
    Represents a boolean field in Baserow.

    :ivar TYPE: The type of the field, which is 'boolean'.
    :vartype TYPE: str
    """

    TYPE = "boolean"
    _COMPATIBLE_FILTERS = ["boolean", "empty", "not_empty"]

    def __init__(self, name: str, field_data: Dict[str, Any]):
        """
        Initialize a BooleanField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        """
        super().__init__(name, field_data)
        self.logger = logging.getLogger(__name__)

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this BooleanField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS

    def validate_value(self, value: bool) -> None:
        """
        Validate the value for a BooleanField.

        :param value: The boolean value to be validated.
        :type value: bool
        :raises ValueError: If the value is not of boolean type.
        """
        if not isinstance(value, bool):
            self.logger.error(
                f"Expected a boolean value for BooleanField but got {type(value)}"
            )
            raise ValueError(
                f"Expected a boolean value for BooleanField but got {type(value)}"
            )


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
        "lower_than",
        "is_even_and_whole",
        "empty",
        "not_empty",
    ]

    def __init__(self, name: str, field_data: Dict[str, Any]):
        """
        Initialize a NumberField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        """
        super().__init__(name, field_data)
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

    def validate_value(self, value: Union[int, float]) -> None:
        """
        Validate the value for a NumberField.

        :param value: The number value to be validated.
        :type value: Union[int, float]
        :raises ValueError: If the value doesn't match the expected type or constraints.
        """
        if value is None:
            return
        elif not isinstance(value, (int, float)):
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


class RatingField(Field):
    """
    Represents a rating field in Baserow.

    :ivar TYPE: The type of the field, which is 'rating'.
    :vartype TYPE: str
    """

    TYPE = "rating"
    _COMPATIBLE_FILTERS = ["equal", "not_equal", "higher_than", "lower_than"]

    def __init__(self, name: str, field_data: Dict[str, Any]):
        """
        Initialize a RatingField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        """
        super().__init__(name, field_data)
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


class BaseDateField(Field):
    """
    Represents a base date field in Baserow.

    :ivar TYPE: The type of the field, which is 'base_date'.
    :vartype TYPE: str
    """

    TYPE = "base_date"

    def __init__(self, name: str, field_data: Dict[str, Any]):
        """
        Initialize a BaseDateField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        """
        super().__init__(name, field_data)

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
            raise ValueError(
                f"Invalid date_format: {self.date_format}. Expected one of ['US', 'EU', 'ISO']."
            )

        if self.date_time_format not in ["12", "24"]:
            self.logger.error(
                f"Invalid date_time_format: {self.date_time_format}. Expected one of ['12', '24']."
            )
            raise ValueError(
                f"Invalid date_time_format: {self.date_time_format}. Expected one of ['12', '24']."
            )

    def validate_value(self, value: str) -> None:
        """
        Validate the date or datetime value based on the field's attributes.

        :param value: The date or datetime value to be validated.
        :type value: str
        :raises ValueError: If the value doesn't match the expected format.
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
                raise ValueError(f"Invalid date format for {self.TYPE}: {value}")
        else:
            # If only date is expected but value contains time, strip the time portion
            if "T" in value:
                value = value.split("T")[0]

            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                self.logger.error(f"Invalid date format for {self.TYPE}: {value}")
                raise ValueError(f"Invalid date format for {self.TYPE}: {value}")


class DateField(BaseDateField):
    """
    Represents a date-only field in Baserow.

    :ivar TYPE: The type of the field, which is 'date'.
    :vartype TYPE: str
    """

    TYPE = "date"
    _COMPATIBLE_FILTERS = [
        "date_equal",
        "date_not_equal",
        "date_equals_today",
        "date_before_today",
        "date_after_today",
        "date_within_days",
        "date_within_weeks",
        "date_within_months",
        "date_equals_days_ago",
        "date_equals_months_ago",
        "date_equals_years_ago",
        "date_equals_week",
        "date_equals_month",
        "date_equals_year",
        "date_equals_day_of_month",
        "date_before",
        "date_before_or_equal",
        "date_after",
        "date_after_or_equal",
        "date_after_days_ago",
        "contains",
        "contains_not",
        "empty",
        "not_empty",
    ]

    def __init__(self, name: str, field_data: Dict[str, Any]):
        """
        Initialize a DateField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        """
        super().__init__(name, field_data)
        self.logger = logging.getLogger(__name__)

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this DateField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS


class LastModifiedField(BaseDateField):
    """
    Represents a field in Baserow that indicates the last modified date.

    :ivar TYPE: The type of the field, which is 'last_modified'.
    :vartype TYPE: str
    """

    TYPE = "last_modified"
    _COMPATIBLE_FILTERS = [
        "date_equal",
        "date_not_equal",
        "date_equals_today",
        "date_before_today",
        "date_after_today",
        "date_within_days",
        "date_within_weeks",
        "date_within_months",
        "date_equals_days_ago",
        "date_equals_months_ago",
        "date_equals_years_ago",
        "date_equals_week",
        "date_equals_month",
        "date_equals_year",
        "date_equals_day_of_month",
        "date_before",
        "date_before_or_equal",
        "date_after",
        "date_after_or_equal",
        "date_after_days_ago",
        "contains",
        "contains_not",
        "empty",
        "not_empty",
    ]

    def __init__(self, name: str, field_data: Dict[str, Any]):
        """
        Initialize a LastModifiedField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        """
        super().__init__(name, field_data)
        self.logger = logging.getLogger(__name__)

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this LastModifiedField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS

    @property
    def is_read_only(self) -> bool:
        """
        Determine if the LastModifiedField is read-only.

        :return: True, as this field type is always read-only.
        :rtype: bool
        """
        return True


class CreatedOnField(BaseDateField):
    """
    Represents a field in Baserow that indicates the creation date.

    :ivar TYPE: The type of the field, which is 'created_on'.
    :vartype TYPE: str
    """

    TYPE = "created_on"
    _COMPATIBLE_FILTERS = [
        "date_equal",
        "date_not_equal",
        "date_equals_today",
        "date_before_today",
        "date_after_today",
        "date_within_days",
        "date_within_weeks",
        "date_within_months",
        "date_equals_days_ago",
        "date_equals_months_ago",
        "date_equals_years_ago",
        "date_equals_week",
        "date_equals_month",
        "date_equals_year",
        "date_equals_day_of_month",
        "date_before",
        "date_before_or_equal",
        "date_after",
        "date_after_or_equal",
        "date_after_days_ago",
        "contains",
        "contains_not",
        "empty",
        "not_empty",
    ]

    def __init__(self, name: str, field_data: Dict[str, Any]):
        """
        Initialize a CreatedOnField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        """
        super().__init__(name, field_data)
        self.logger = logging.getLogger(__name__)

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this CreatedOnField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS

    @property
    def is_read_only(self) -> bool:
        """
        Determine if the CreatedOnField is read-only.

        :return: True, as this field type is always read-only.
        :rtype: bool
        """
        return True

    """
    Represents a field in Baserow that indicates the creation date.

    :ivar TYPE: The type of the field, which is 'created_on'.
    :vartype TYPE: str
    """

    TYPE = "created_on"

    def __init__(self, name: str, field_data: Dict[str, Any]):
        """
        Initialize a CreatedOnField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        """
        super().__init__(name, field_data)

    @property
    def is_read_only(self) -> bool:
        """
        Determine if the CreatedOnField is read-only.

        :return: True, as this field type is always read-only.
        :rtype: bool
        """
        return True


class FileField(Field):
    """
    Represents a field in Baserow that handles file data.

    :ivar TYPE: The type of the field, which is 'file'.
    :vartype TYPE: str
    """

    TYPE = "file"
    _COMPATIBLE_FILTERS = ["filename_contains", "has_file_type", "empty", "not_empty"]

    def __init__(self, name: str, field_data: Dict[str, Any]):
        """
        Initialize a FileField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        """
        super().__init__(name, field_data)
        self.logger = logging.getLogger(__name__)

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this FileField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS

    def validate_value(self, value: List[Dict[str, Any]]) -> None:
        """
        Validates the value for a FileField.

        :param value: A list of file objects to validate.
        :type value: List[Dict[str, Any]]

        :raises ValueError: If the value is not a list or if a file object is missing
                            the 'name' attribute.
        """
        if not isinstance(value, list):
            self.logger.error(f"Expected a list for FileField but got {type(value)}")
            raise ValueError(f"Expected a list for FileField but got {type(value)}")

        for file_obj in value:
            if not file_obj.get("name"):
                self.logger.error("File object is missing the 'name' attribute.")
                raise ValueError("File object is missing the 'name' attribute.")

    def format_for_api(self, value: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Formats the value for API submission. For FileField, it returns the list of file
        objects as-is.

        :param value: A list of file objects.
        :type value: List[Dict[str, Any]]

        :return: The same list of file objects.
        :rtype: List[Dict[str, Any]]
        """
        return value


class SingleSelectField(Field):
    """
    Utility method to retrieve an option by its id or value.

    :param value: The id or value of the option to retrieve.
    :type value: Union[int, str]
    :return: The option if found, otherwise None.
    :rtype: Optional[Dict[str, Any]]
    """

    TYPE = "single_select"
    _COMPATIBLE_FILTERS = [
        "contains",
        "contains_not",
        "contains_word",
        "doesnt_contain_word",
        "single_select_equal",
        "single_select_not_equal",
        "empty",
        "not_empty",
    ]

    def __init__(self, name: str, field_data: Dict[str, Any]):
        """
        Initializes a SingleSelectField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        """
        super().__init__(name, field_data)
        self.logger = logging.getLogger(__name__)
        if "select_options" not in field_data or not isinstance(
            field_data["select_options"], list
        ):
            self.logger.error(
                "Invalid or missing select_options provided for SingleSelectField initialization."
            )
            raise ValueError("select_options should be a non-empty list in field_data.")

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this SingleSelectField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS

    @property
    def options(self) -> List[str]:
        """
        Retrieve a list of select option values from the field_data.

        :return: List of select option values.
        :rtype: List[str]
        """
        return [option["value"] for option in self.field_data["select_options"]]

    @property
    def options_details(self) -> List[Dict[str, Any]]:
        """
        Retrieve a list including details like id, value, color of each select_option.

        :return: List of detailed select_options.
        :rtype: List[Dict[str, Any]]
        """
        return self.field_data["select_options"]

    def _get_option_by_id_or_value(
        self, value: Union[int, str]
    ) -> Optional[Dict[str, Any]]:
        """
        Utility method to retrieve an option by its id or value.

        :param value: The id or value of the option to retrieve.
        :type value: Union[int, str]
        :return: The option if found, otherwise None.
        :rtype: Optional[Dict[str, Any]]
        """
        for option in self.options_details:
            if option["id"] == value or option["value"] == value:
                return option
        return None

    def validate_value(self, value: Union[int, str]) -> None:
        """
        Validates the value for a SingleSelectField.

        :param value: The value to validate.
        :type value: Union[int, str]
        :raises ValueError: If the provided value doesn't match any select option.
        """
        if value is not None:
            option = self._get_option_by_id_or_value(value)
            if not option:
                raise ValueError(
                    f"The provided value '{value}' doesn't match any select option."
                )

    def format_for_api(self, value: Union[int, str]) -> Union[int, str, None]:
        """
        Formats the value for API submission.

        :param value: The value to format.
        :type value: Union[int, str]
        :return: The id of the matching option for API submission, or None if value is None.
        :rtype: Union[int, str, None]
        :raises ValueError: If the provided value doesn't match any select option.
        """
        if value is None:
            return value

        option = self._get_option_by_id_or_value(value)
        if not option:
            raise ValueError(
                f"The provided value '{value}' doesn't match any select option."
            )

        return option["id"]  # Return the id for API submission


class MultipleSelectField(Field):
    """
    Represents a multiple-select field allowing the user to select multiple options from a predefined set of options.

    :ivar TYPE: The type of the field, which is 'multiple_select'.
    :vartype TYPE: str
    """

    TYPE = "multiple_select"
    _COMPATIBLE_FILTERS = [
        "contains",
        "contains_not",
        "contains_word",
        "doesnt_contain_word",
        "multiple_select_has",
        "multiple_select_has_not",
        "empty",
        "not_empty",
    ]

    def __init__(self, name: str, field_data: Dict[str, Any]):
        """
        Initializes a MultipleSelectField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        """
        super().__init__(name, field_data)
        self.logger = logging.getLogger(__name__)
        if "select_options" not in field_data or not isinstance(
            field_data["select_options"], list
        ):
            self.logger.error(
                "Invalid or missing select_options provided for MultipleSelectField initialization."
            )
            raise ValueError("select_options should be a non-empty list in field_data.")

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this MultipleSelectField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS

    @property
    def options(self) -> List[str]:
        """
        Retrieve a list of select option values from the field_data.

        :return: List of select option values.
        :rtype: List[str]
        """
        return [option["value"] for option in self.field_data["select_options"]]

    @property
    def options_details(self) -> List[Dict[str, Any]]:
        """
        Retrieve a list including details like id, value, color of each select_option.

        :return: List of detailed select_options.
        :rtype: List[Dict[str, Any]]
        """
        return self.field_data["select_options"]

    def _get_option_by_id_or_value(
        self, value: Union[int, str]
    ) -> Optional[Dict[str, Any]]:
        """
        Utility method to retrieve an option by its id or value.

        :param value: The id or value of the option to retrieve.
        :type value: Union[int, str]
        :return: The option if found, otherwise None.
        :rtype: Optional[Dict[str, Any]]
        """
        for option in self.options_details:
            if option["id"] == value or option["value"] == value:
                return option
        return None

    def validate_value(self, values: List[Union[int, str]]) -> None:
        """
        Validates the values for a MultipleSelectField.

        :param values: The list of values to validate.
        :type values: List[Union[int, str]]
        :raises ValueError: If the provided values list contains a value that doesn't match any select option.
        """
        if values is None:
            return

        if not isinstance(values, list):
            raise ValueError(
                "The provided value should be a list for a MultipleSelectField."
            )

        for value in values:
            option = self._get_option_by_id_or_value(value)
            if not option:
                raise ValueError(
                    f"The provided value '{value}' doesn't match any select option."
                )

    def format_for_api(self, values: List[Union[int, str]]) -> List[Union[int, str]]:
        """
        Formats the values for API submission.

        :param values: The list of values to format.
        :type values: List[Union[int, str]]
        :return: A list of ids of the matching options for API submission.
        :rtype: List[Union[int, str]]
        :raises ValueError: If the provided values list contains a value that doesn't match any select option.
        """
        if values is None:
            return values

        if not isinstance(values, list):
            raise ValueError(
                "The provided value should be a list for a MultipleSelectField."
            )

        formatted_values = []
        for value in values:
            option = self._get_option_by_id_or_value(value)
            if not option:
                raise ValueError(
                    f"The provided value '{value}' doesn't match any select option."
                )
            formatted_values.append(option["id"])

        return formatted_values


class FormulaField(Field):
    """
    Represents a field that computes its value based on a formula.

    :ivar TYPE: The type of the field, which is 'formula'.
    :vartype TYPE: str
    """

    TYPE = "formula"
    _COMPATIBLE_FILTERS = []

    def __init__(self, name: str, field_data: Dict[str, Any]):
        """
        Initializes a FormulaField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        """
        super().__init__(name, field_data)

        # Attributes specific to the FormulaField
        self._formula = field_data.get("formula")
        self._formula_type = field_data.get("formula_type")
        self._error = field_data.get("error")
        self._array_formula_type = field_data.get("array_formula_type")

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this FormulaField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS

    @property
    def formula(self) -> Optional[str]:
        """
        Retrieve the formula of the field.

        :return: The formula of the field.
        :rtype: Optional[str]
        """

        return self._formula

    @property
    def formula_type(self) -> Optional[str]:
        """
        Retrieve the formula type of the field.

        :return: The formula type of the field.
        :rtype: Optional[str]
        """

        return self._formula_type

    @property
    def error(self) -> Optional[str]:
        """
        Retrieve the error (if any) associated with the formula.

        :return: The error associated with the formula.
        :rtype: Optional[str]
        """

        return self._error

    @property
    def array_formula_type(self) -> Optional[str]:
        """
        Retrieve the array formula type of the field.

        :return: The array formula type of the field.
        :rtype: Optional[str]
        """

        return self._array_formula_type

    @property
    def is_read_only(self) -> bool:
        """
        Determine if the field is read-only.

        :return: Always returns True for a FormulaField.
        :rtype: bool
        """

        return True


class TableLinkField(Field):
    """
    Represents a field that links to rows in another table.

    :ivar TYPE: The type of the field, which is 'link_row'.
    :vartype TYPE: str
    """

    TYPE = "link_row"
    _COMPATIBLE_FILTERS = [
        "link_row_has",
        "link_row_has_not",
        "link_row_contains",
        "link_row_not_contains",
        "empty",
        "not_empty",
    ]

    def __init__(self, name: str, field_data: Dict[str, Any]):
        """
        Initializes a TableLinkField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        :raises ValueError: If the field type doesn't match the expected type.
        """
        super().__init__(name, field_data)
        if self.type != self.TYPE:
            self.logger.error(
                f"Invalid type for TableLinkField. Expected {self.TYPE}, got {self.type}."
            )
            raise ValueError(
                f"Invalid type for TableLinkField. Expected {self.TYPE}, got {self.type}."
            )

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this TableLinkField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """

        return self._COMPATIBLE_FILTERS

    def format_for_api(self, value: List[Union[int, str]]) -> List[Union[int, str]]:
        """
        Format the value for API submission. This method accepts a list of either integers
        (identifying rows in the linked table) or strings (values of the primary field in the
        linked table).

        :param value: A list containing either integers (row identifiers in the linked table)
                    or strings (values of the primary field in the linked table).
        :type value: List[Union[int, str]]
        :return: A list containing row identifiers or primary field values formatted for API submission.
        :rtype: List[Union[int, str]]
        :raises ValueError: If the provided value is not a list or if its entries are not integers or strings.
        """

        # Ensure the value is a list
        if not isinstance(value, list):
            self.logger.error("Value provided for TableLinkField should be a list.")
            raise ValueError("Value provided for TableLinkField should be a list.")

        # Validate each entry in the list to be either an integer or string
        for entry in value:
            if not isinstance(entry, (int, str)):
                self.logger.error(
                    "Each entry in the list should be an integer or string."
                )
                raise ValueError(
                    "Each entry in the list should be an integer or string."
                )

        # Since the API expects a simple list of integers or strings, return the value as-is
        return value

    @property
    def link_row_table_id(self) -> Optional[int]:
        """
        Retrieve the link_row_table_id of the field from field_data.

        :return: The link_row_table_id of the field.
        :rtype: Optional[int]
        """
        return self.field_data.get("link_row_table_id", None)

    @property
    def link_row_related_field_id(self) -> Optional[int]:
        """
        Retrieve the link_row_related_field_id of the field from field_data.

        :return: The link_row_related_field_id of the field.
        :rtype: Optional[int]
        """
        return self.field_data.get("link_row_related_field_id", None)

    @property
    def link_row_table(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve the link_row_table from field_data.

        :return: Details of the linked table.
        :rtype: Optional[Dict[str, Any]]
        """

        return self.field_data.get("link_row_table", None)

    @property
    def link_row_related_field(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve the link_row_related_field from field_data.

        :return: Details of the related field in the linked table.
        :rtype: Optional[Dict[str, Any]]
        """

        return self.field_data.get("link_row_related_field", None)


class CountField(Field):
    """
    Represents a field connected to a link to table field which returns the number of relations.

    :ivar TYPE: The type of the field, which is 'count'.
    :vartype TYPE: str
    """

    TYPE = "count"
    _COMPATIBLE_FILTERS = [
        "equal",
        "not_equal",
        "contains",
        "contains_not",
        "higher_than",
        "lower_than",
        "is_even_and_whole",
        "empty",
        "not_empty",
    ]

    def __init__(self, name: str, field_data: Dict[str, Any]):
        """
        Initializes a CountField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        """
        super().__init__(name, field_data)

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this CountField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS

    @property
    def is_read_only(self) -> bool:
        """
        Determine if the field is read-only.

        :return: Always True for CountField.
        :rtype: bool
        """
        return True

    def validate_value(self, value: int):
        """
        Validate the value for a CountField.

        :param value: The value to validate.
        :type value: int
        :raises ValueError: If the value is not an integer or if it's negative.
        """
        if not isinstance(value, int):
            raise ValueError(
                f"Expected an integer value for CountField but got {type(value)}"
            )
        if value < 0:
            raise ValueError("CountField value cannot be negative.")

    @property
    def through_field_id(self) -> Optional[str]:
        """
        Retrieve the through_field_id of the field from field_data.

        :return: The id of the linking field.
        :rtype: Optional[str]
        """

        return self.field_data.get("through_field_id", None)


class LookupField(Field):
    """
    Represents a field field connected to a link to table field
    which returns an array of values and row ids from the chosen
    lookup field in the linked table.

    :ivar TYPE: The type of the field, which is 'lookup'.
    :vartype TYPE: str
    """

    TYPE = "lookup"
    _COMPATIBLE_FILTERS = []

    def __init__(self, name: str, field_data: Dict[str, Any]):
        """
        Initializes a LookupField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        :raises ValueError: If the field is not read-only.
        """
        super().__init__(name, field_data)

        if not self.is_read_only:
            self.logger.error("LookupField should be read-only.")
            raise ValueError("LookupField should be read-only.")

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this LookupField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """

        return self._COMPATIBLE_FILTERS

    @property
    def through_field_id(self) -> Optional[int]:
        """
        Retrieve the through_field_id of the field from field_data.

        :return: The id of the linking field.
        :rtype: Optional[int]
        """

        return self.field_data.get("through_field_id", None)

    @property
    def through_field_name(self) -> Optional[int]:
        """
        Retrieve the through_field_name of the field from field_data.

        :return: The name of the linking field.
        :rtype: Optional[int]
        """

        return self.field_data.get("through_field_name", None)

    @property
    def target_field_id(self) -> Optional[int]:
        """
        Retrieve the target_field_id of the field from field_data.

        :return: The id of the target field.
        :rtype: Optional[int]
        """

        return self.field_data.get("target_field_id", None)

    @property
    def target_field_name(self) -> Optional[str]:
        """
        Retrieve the target_field_name of the field from field_data.

        :return: The name of the target field.
        :rtype: Optional[str]
        """

        return self.field_data.get("target_field_name", None)


class MultipleCollaboratorsField(Field):
    """
    Represents a list of Baserow collaborators.

    :ivar TYPE: The type of the field, which is 'multiple_collaborators'.
    :vartype TYPE: str
    """

    TYPE = "multiple_collaborators"
    _COMPATIBLE_FILTERS = [
        "multiple_collaborators_has",
        "multiple_collaborators_has_not",
        "empty",
        "not_empty",
    ]

    def __init__(self, name: str, field_data: Dict[str, Any]):
        """
        Initializes a MultipleCollaboratorsField object.

        :param name: The name of the field.
        :type name: str
        :param field_data: A dictionary containing the field's data and attributes.
        :type field_data: Dict[str, Any]
        """
        super().__init__(name, field_data)

    @property
    def compatible_filters(self) -> List[str]:
        """
        Get the list of compatible filters for this MultipleCollaboratorsField.

        :return: The list of compatible filters.
        :rtype: List[str]
        """
        return self._COMPATIBLE_FILTERS

    @property
    def notify_user_when_added(self) -> bool:
        """
        Determine if the user should be notified when added.

        :return: True if the user should be notified, False otherwise.
        :rtype: bool
        """
        return self.field_data.get("notify_user_when_added", False)

    def format_for_api(self, value: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format the value for API submission. Accepts an array of objects where each object contains a user's id.

        :param value: A list of dictionaries representing collaborator data.
        :type value: List[Dict[str, Any]]
        :return: The list of collaborator data formatted for API submission.
        :rtype: List[Dict[str, Any]]
        :raises ValueError: If the provided value is not a list or if the format is incorrect.
        """
        if not isinstance(value, list):
            raise ValueError(
                f"Expected a list of collaborator data for MultipleCollaboratorsField but got {type(value)}"
            )
        return value  # Return value as-is since it's already in the expected format

    def validate_value(self, value: List[Dict[str, Any]]):
        """
        Validate the value for a MultipleCollaboratorsField.

        :param value: A list of dictionaries representing collaborator data.
        :type value: List[Dict[str, Any]]
        :raises ValueError: If the provided value is not a list or if the format is incorrect.
        """
        if not isinstance(value, list):
            raise ValueError(
                f"Expected a list for MultipleCollaboratorsField but got {type(value)}"
            )
        for collaborator in value:
            if not isinstance(collaborator, dict) or "id" not in collaborator:
                raise ValueError(
                    "Each collaborator in MultipleCollaboratorsField should be a dictionary with an 'id' key"
                )


class FieldList:
    """
    Represents a list of Field objects.

    :ivar fields: A list containing the Field objects.
    :vartype fields: List[Field]
    :ivar logger: A logger instance for the class.
    :vartype logger: logging.Logger
    """

    def __init__(self, fields: List[Field]) -> None:
        """
        Initialize a FieldList with a list of Field objects.

        :param fields: A list of Field objects.
        :type fields: List[Field]
        """
        self.fields = fields
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Initialized FieldList with {len(fields)} fields.")

    def __repr__(self) -> str:
        """
        Provide a string representation of the FieldList object.

        :return: A string representing the FieldList.
        :rtype: str
        """
        max_fields_to_show = 5
        fields_names = [field.name for field in self.fields]

        if len(fields_names) > max_fields_to_show:
            fields_names = fields_names[:max_fields_to_show] + ["..."]

        fields_str = ", ".join(fields_names)
        return f"FieldList({len(self.fields)} fields: [{fields_str}])"

    def __getitem__(self, field_name: str) -> Field:
        """
        Retrieve a field by its name.

        :param field_name: The name of the desired field.
        :type field_name: str
        :return: The desired Field object.
        :rtype: Field
        :raises KeyError: If the field_name doesn't match any fields in the list.
        """
        for field in self.fields:
            if field.name == field_name:
                return field
        self.logger.error(f"Field '{field_name}' not found.")
        raise KeyError(f"Field '{field_name}' not found.")

    def __iter__(self) -> Iterator[Field]:
        """
        Return an iterator over the fields.

        :return: An iterator over the Field objects.
        :rtype: Iterator[Field]
        """
        return iter(self.fields)

    def __len__(self) -> int:
        """
        Return the number of fields in the list.

        :return: The number of fields.
        :rtype: int
        """
        return len(self.fields)

    def __contains__(self, field_name: str) -> bool:
        """
        Check if a field with the given name exists in the FieldList.

        :param field_name: The name of the field to check.
        :type field_name: str
        :return: True if the field exists, otherwise False.
        :rtype: bool
        """
        exists = any(field.name == field_name for field in self.fields)
        if not exists:
            self.logger.warning(f"Field '{field_name}' not found in FieldList.")
        return exists
