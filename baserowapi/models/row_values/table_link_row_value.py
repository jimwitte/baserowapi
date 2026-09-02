from typing import Any, Optional

from baserowapi.exceptions import InvalidRowValueError
from baserowapi.models.fields import TableLinkField
from baserowapi.models.row_values.row_value import RowValue
from baserowapi.models.values import LinkedRow


class TableLinkRowValue(RowValue):
    """Compatibility facade for field-owned linked-row semantics."""

    def __init__(
        self,
        field: TableLinkField,
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ) -> None:
        super().__init__(field, raw_value if raw_value is not None else [], client)
        if not isinstance(field, TableLinkField):
            raise InvalidRowValueError(
                f"Expected TableLinkField, got {type(field).__name__}."
            )

    @property
    def value(self) -> list[LinkedRow]:
        return self.field.decode_value(self._raw_value)

    @value.setter
    def value(self, new_value: Any) -> None:
        self.field.validate_value(new_value)
        self._raw_value = self.field.decode_value(new_value)
