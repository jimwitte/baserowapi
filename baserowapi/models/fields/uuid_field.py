from typing import Any
from uuid import UUID

from baserowapi.exceptions import FieldValueError
from baserowapi.models.fields.field import Field


class UUIDField(Field):
    """A read-only persistent Baserow UUID."""

    TYPE = "uuid"
    _COMPATIBLE_FILTERS = ["equal", "not_equal"]

    @property
    def compatible_filters(self) -> list[str]:
        return self._COMPATIBLE_FILTERS

    @property
    def is_read_only(self) -> bool:
        return True

    def parse_value(self, value: Any) -> UUID:
        """Parse a returned UUID string without changing ordinary row reads."""
        if not isinstance(value, str):
            raise FieldValueError("A Baserow UUID value must be a string.")
        try:
            return UUID(value)
        except ValueError as error:
            raise FieldValueError(f"Invalid Baserow UUID value: {value!r}.") from error
