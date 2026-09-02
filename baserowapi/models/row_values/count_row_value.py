from typing import Any, Optional

from baserowapi.exceptions import InvalidRowValueError, ReadOnlyValueError
from baserowapi.models.fields import CountField
from baserowapi.models.row_values.row_value import RowValue


class CountRowValue(RowValue):
    """Compatibility facade for field-owned count-result semantics."""

    def __init__(
        self,
        field: CountField,
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ) -> None:
        super().__init__(field, raw_value, client)
        if not isinstance(field, CountField):
            raise InvalidRowValueError(
                f"Expected CountField, got {type(field).__name__}."
            )

    @property
    def value(self) -> Any:
        return self.field.decode_value(self._raw_value)

    @value.setter
    def value(self, new_value: Any) -> None:
        raise ReadOnlyValueError("Cannot set value for a read-only CountRowValue.")
