"""Baserow row model backed directly by Field semantics."""

from collections.abc import Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Optional, Union

if TYPE_CHECKING:
    from baserowapi.baserow import Baserow as Client
    from baserowapi.models.table import Table


class Row:
    """One Baserow row with decoded and raw field-value access."""

    def __init__(
        self, row_data: Mapping[str, Any], table: "Table", client: "Client"
    ) -> None:
        self.table = table
        self.table_id = table.id
        self.client = client
        self._replace_data(row_data)

    def _replace_data(self, row_data: Mapping[str, Any]) -> None:
        if not isinstance(row_data, Mapping):
            raise TypeError("row_data must be a mapping.")
        self._row_data = dict(row_data)
        self.id: Optional[int] = self._row_data.get("id")
        self.order: Any = self._row_data.get("order")
        self._raw_values = {
            name: value
            for name, value in self._row_data.items()
            if name not in {"id", "order"}
        }
        self._raw_values_view = MappingProxyType(self._raw_values)
        self._decoded_values: Optional[Mapping[str, Any]] = None

    @property
    def raw_values(self) -> Mapping[str, Any]:
        """Return a shallow read-only mapping of raw Baserow field values."""
        return self._raw_values_view

    @property
    def values(self) -> Mapping[str, Any]:
        """Return a shallow read-only mapping of Field-decoded values."""
        if self._decoded_values is None:
            decoded = {
                name: self.table.fields[name].decode_value(raw_value)
                for name, raw_value in self._raw_values.items()
            }
            self._decoded_values = MappingProxyType(decoded)
        return self._decoded_values

    def __repr__(self) -> str:
        return f"Row id {self.id} of table {self.table_id}"

    def __getitem__(self, field_name: str) -> Any:
        if field_name not in self._raw_values:
            raise KeyError(f"Field {field_name!r} was not returned for this row.")
        field = self.table.fields[field_name]
        return field.decode_value(self._raw_values[field_name])

    def __contains__(self, field_name: str) -> bool:
        return field_name in self._raw_values

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Row)
            and self.id == other.id
            and self.table_id == other.table_id
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a mutable top-level copy of the decoded field values."""
        return dict(self.values)

    def update(self, values: Mapping[str, Any]) -> "Row":
        """Persist an explicit field-value mapping and synchronize this Row."""
        updated = self.table.update_row(self.id, values)
        self._replace_data(updated._row_data)
        return self

    def delete(self) -> bool:
        """Delete this row through its Table."""
        return self.table.delete_row(self.id)

    def move(self, before_id: Optional[Union[int, str]] = None) -> "Row":
        """Move this row through its Table and synchronize this object."""
        moved = self.table.move_row(self.id, before_id=before_id)
        self._replace_data(moved._row_data)
        return self
