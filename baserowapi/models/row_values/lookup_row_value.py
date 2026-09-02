from typing import Any, Optional

from baserowapi.exceptions import InvalidRowValueError, ReadOnlyValueError
from baserowapi.models.fields import LookupField
from baserowapi.models.row_values.row_value import RowValue
from baserowapi.models.values import LookupEntry


class LookupRowValue(RowValue):
    """Compatibility facade for field-owned lookup-entry decoding."""

    def __init__(
        self,
        field: LookupField,
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ) -> None:
        super().__init__(field, raw_value if raw_value is not None else [], client)
        if not isinstance(field, LookupField):
            raise InvalidRowValueError(
                f"Expected LookupField, got {type(field).__name__}."
            )

    @property
    def value(self) -> list[LookupEntry]:
        return self.field.decode_value(self._raw_value)

    @value.setter
    def value(self, new_value: Any) -> None:
        raise ReadOnlyValueError("Cannot set value for a read-only LookupRowValue.")
