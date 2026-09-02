from typing import Any, Optional

from baserowapi.exceptions import InvalidRowValueError
from baserowapi.models.fields import SingleSelectField
from baserowapi.models.row_values.row_value import RowValue
from baserowapi.models.values import SelectOption


class SingleSelectRowValue(RowValue):
    """Compatibility facade for field-owned single-select semantics."""

    def __init__(
        self,
        field: SingleSelectField,
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ) -> None:
        super().__init__(field, raw_value, client)
        if not isinstance(field, SingleSelectField):
            raise InvalidRowValueError(
                f"Expected SingleSelectField, got {type(field).__name__}."
            )

    @property
    def options(self) -> list[SelectOption]:
        return self.field.options

    @property
    def value(self) -> Optional[SelectOption]:
        return self.field.decode_value(self._raw_value)

    @value.setter
    def value(self, new_value: Any) -> None:
        self.field.validate_value(new_value)
        self._raw_value = self.field.decode_value(new_value)
