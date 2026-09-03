from datetime import date, datetime, timezone, tzinfo
import re
from typing import Any, Dict, Optional, Union
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from baserowapi.exceptions import FieldValidationError, FieldValueError
from baserowapi.models.fields.field import Field


DateValue = Union[str, date, datetime, None]


class BaseDateField(Field):
    """Common Baserow semantics for date and datetime fields."""

    _COMPATIBLE_FILTERS = (
        "date_is",
        "date_is_not",
        "date_is_before",
        "date_is_on_or_before",
        "date_is_after",
        "date_is_on_or_after",
        "date_is_within",
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
    )
    _DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    _DATETIME_PATTERN = re.compile(
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
    )
    _DATE_DISPLAY_FORMATS = {
        "US": "%m-%d-%Y",
        "EU": "%d-%m-%Y",
        "ISO": "%Y-%m-%d",
    }
    _TIME_DISPLAY_FORMATS = {"12": "%I:%M:%S %p", "24": "%H:%M:%S"}

    def __init__(self, name: str, field_data: Dict[str, Any], client=None) -> None:
        super().__init__(name, field_data, client)

        self.date_format: str = field_data.get("date_format", "EU")
        self.date_include_time: bool = field_data.get("date_include_time", True)
        self.date_time_format: str = field_data.get("date_time_format", "24")
        self.date_show_tzinfo: bool = field_data.get("date_show_tzinfo", False)
        self.date_force_timezone: Optional[str] = field_data.get(
            "date_force_timezone"
        )

        if self.date_format not in self._DATE_DISPLAY_FORMATS:
            raise FieldValidationError(
                f"Invalid date_format {self.date_format!r}; expected US, EU, or ISO."
            )
        if self.date_time_format not in self._TIME_DISPLAY_FORMATS:
            raise FieldValidationError(
                f"Invalid date_time_format {self.date_time_format!r}; expected 12 or 24."
            )

    def _parse_value(self, value: DateValue, error_type):
        if value is None:
            return None

        if self.date_include_time:
            if isinstance(value, datetime):
                parsed = value
            elif isinstance(value, str) and self._DATETIME_PATTERN.fullmatch(value):
                iso_value = value[:-1] + "+00:00" if value.endswith("Z") else value
                try:
                    parsed = datetime.fromisoformat(iso_value)
                except ValueError as error:
                    raise error_type(
                        f"Invalid ISO datetime for field {self.name!r}: {value!r}."
                    ) from error
            else:
                raise error_type(
                    f"Field {self.name!r} requires an ISO datetime with an explicit "
                    "UTC offset or Z suffix."
                )

            if parsed.tzinfo is None or parsed.utcoffset() is None:
                raise error_type(
                    f"Field {self.name!r} requires a timezone-aware datetime."
                )
            return parsed

        if isinstance(value, datetime):
            raise error_type(
                f"Field {self.name!r} is date-only and does not accept a datetime."
            )
        if isinstance(value, date):
            return value
        if isinstance(value, str) and self._DATE_PATTERN.fullmatch(value):
            try:
                return date.fromisoformat(value)
            except ValueError as error:
                raise error_type(
                    f"Invalid ISO date for field {self.name!r}: {value!r}."
                ) from error
        raise error_type(
            f"Field {self.name!r} requires an ISO date in YYYY-MM-DD form."
        )

    def validate_value(self, value: DateValue) -> None:
        """Validate a strict Baserow ISO date or datetime write value."""
        self._parse_value(value, FieldValidationError)

    def encode_value(self, value: DateValue) -> Optional[str]:
        """Encode a strict date value without guessing missing information."""
        parsed = self._parse_value(value, FieldValidationError)
        if parsed is None:
            return None
        if isinstance(parsed, datetime):
            encoded = parsed.isoformat()
            if parsed.utcoffset() == timezone.utc.utcoffset(parsed):
                encoded = encoded.removesuffix("+00:00") + "Z"
            return encoded
        return parsed.isoformat()

    def parse_value(self, value: DateValue) -> Union[date, datetime, None]:
        """Explicitly parse a Baserow ISO value into a Python date or datetime."""
        return self._parse_value(value, FieldValueError)

    def _display_timezone(
        self, target_timezone: Optional[Union[str, tzinfo]]
    ) -> Optional[tzinfo]:
        timezone_value = target_timezone or self.date_force_timezone
        if timezone_value is None:
            return None
        if isinstance(timezone_value, str):
            try:
                return ZoneInfo(timezone_value)
            except ZoneInfoNotFoundError as error:
                raise FieldValueError(
                    f"Unknown timezone {timezone_value!r} for field {self.name!r}."
                ) from error
        if isinstance(timezone_value, tzinfo):
            return timezone_value
        raise FieldValueError("Display timezone must be a timezone name or tzinfo object.")

    def format_value(
        self,
        value: DateValue,
        *,
        target_timezone: Optional[Union[str, tzinfo]] = None,
    ) -> Optional[str]:
        """Format a value using Baserow's date display metadata.

        Datetimes retain their supplied offset unless the field forces a
        timezone or the caller supplies ``target_timezone``.
        """
        parsed = self.parse_value(value)
        if parsed is None:
            return None

        date_format = self._DATE_DISPLAY_FORMATS[self.date_format]
        if not isinstance(parsed, datetime):
            return parsed.strftime(date_format)

        display_timezone = self._display_timezone(target_timezone)
        if display_timezone is not None:
            parsed = parsed.astimezone(display_timezone)

        formatted = (
            f"{parsed.strftime(date_format)} "
            f"{parsed.strftime(self._TIME_DISPLAY_FORMATS[self.date_time_format])}"
        )
        if self.date_show_tzinfo:
            timezone_name = parsed.tzname() or parsed.strftime("%z")
            formatted = f"{formatted} {timezone_name}"
        return formatted
