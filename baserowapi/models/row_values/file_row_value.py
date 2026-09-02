from typing import Any, Optional

from baserowapi.exceptions import InvalidRowValueError
from baserowapi.models.fields import FileField
from baserowapi.models.row_values.row_value import RowValue


class FileRowValue(RowValue):
    """Compatibility facade for field-owned Baserow file semantics."""

    def __init__(
        self,
        field: FileField,
        client: Optional[Any] = None,
        raw_value: Optional[Any] = None,
    ) -> None:
        super().__init__(field, raw_value if raw_value is not None else [], client)
        if not isinstance(field, FileField):
            raise InvalidRowValueError(f"Expected FileField, got {type(field).__name__}.")
