from typing import Any, Optional

from baserowapi.exceptions import InvalidRowValueError, ReadOnlyValueError
from baserowapi.models.fields import UUIDField
from baserowapi.models.row_values.row_value import RowValue


class UUIDRowValue(RowValue):
    """Compatibility facade for a read-only UUID field."""

    def __init__(
        self,
        field: UUIDField,
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ) -> None:
        super().__init__(field, raw_value, client)
        if not isinstance(field, UUIDField):
            raise InvalidRowValueError(
                f"Expected UUIDField, got {type(field).__name__}."
            )

    @property
    def value(self) -> Any:
        return self.field.decode_value(self._raw_value)

    @value.setter
    def value(self, new_value: Any) -> None:
        raise ReadOnlyValueError("Cannot set value for a read-only UUIDRowValue.")
