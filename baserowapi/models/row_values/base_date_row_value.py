from datetime import date, datetime, time
from typing import Any, Optional, Union

from baserowapi.exceptions import (
    FieldValidationError,
    FieldValueError,
    InvalidRowValueError,
    RowValueOperationError,
)
from baserowapi.models.fields.base_date_field import BaseDateField
from baserowapi.models.row_values.row_value import RowValue


class BaseDateRowValue(RowValue):
    """Compatibility facade for date behavior now owned by ``BaseDateField``."""

    def __init__(
        self,
        field: "BaseDateField",
        raw_value: Optional[str] = None,
        client: Optional[Any] = None,
    ) -> None:
        super().__init__(field, raw_value, client)
        if not isinstance(field, BaseDateField):
            raise InvalidRowValueError(
                "The provided field is not an instance of BaseDateField. "
                f"Received: {type(field).__name__}"
            )

    @property
    def value(self) -> Optional[str]:
        return self.field.decode_value(self._raw_value)

    @value.setter
    def value(self, new_value: Union[date, datetime, str, None]) -> None:
        try:
            self._raw_value = self.field.encode_value(new_value)
        except FieldValidationError as error:
            raise InvalidRowValueError(
                f"Failed to set value for field {self.field.name}. Error: {error}"
            ) from error

    def as_datetime(self) -> Optional[datetime]:
        """Return the value as a datetime for compatibility with earlier releases."""
        try:
            parsed = self.field.parse_value(self._raw_value)
        except FieldValueError as error:
            raise RowValueOperationError(
                f"Failed to parse value for field {self.field.name}. Error: {error}"
            ) from error
        if parsed is None or isinstance(parsed, datetime):
            return parsed
        return datetime.combine(parsed, time.min)

    @property
    def formatted_date(self) -> Optional[str]:
        """Return the value formatted using the field's Baserow display metadata."""
        try:
            return self.field.format_value(self._raw_value)
        except FieldValueError as error:
            raise RowValueOperationError(
                f"Failed to format value for field {self.field.name}. Error: {error}"
            ) from error
