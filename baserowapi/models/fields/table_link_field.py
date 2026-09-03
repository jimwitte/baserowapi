from typing import Any, Optional

from baserowapi.exceptions import (
    FieldDataRetrievalError,
    FieldValidationError,
    FieldValueError,
)
from baserowapi.models.fields.field import Field
from baserowapi.models.values import LinkedRow


class TableLinkField(Field):
    """Baserow metadata and complete-set semantics for a link-row field."""

    TYPE = "link_row"
    _COMPATIBLE_FILTERS = (
        "link_row_has",
        "link_row_has_not",
        "link_row_contains",
        "link_row_not_contains",
        "empty",
        "not_empty",
    )

    @property
    def link_row_table_id(self) -> Optional[int]:
        return self.field_data.get("link_row_table_id")

    @property
    def link_row_related_field_id(self) -> Optional[int]:
        return self.field_data.get("link_row_related_field_id")

    @property
    def link_row_limit_selection_view_id(self) -> Optional[int]:
        return self.field_data.get("link_row_limit_selection_view_id")

    def _decode_link(self, raw_value: Any) -> LinkedRow:
        table_id = self.link_row_table_id
        if table_id is None:
            raise FieldValueError(
                f"Link-row field {self.name!r} has no linked table ID."
            )
        if isinstance(raw_value, LinkedRow):
            return raw_value
        if isinstance(raw_value, dict):
            row_id = raw_value.get("id")
            if row_id is not None and (
                isinstance(row_id, bool) or not isinstance(row_id, int)
            ):
                raise FieldValueError("A linked row ID must be an integer.")
            return LinkedRow(
                table_id=table_id,
                id=row_id,
                value=raw_value.get("value"),
                raw=dict(raw_value),
            )
        if isinstance(raw_value, bool):
            raise FieldValueError("A linked row ID cannot be a boolean.")
        if isinstance(raw_value, int):
            return LinkedRow(table_id, raw_value, raw={"id": raw_value})
        if isinstance(raw_value, str):
            return LinkedRow(table_id, None, raw_value, {"value": raw_value})
        raise FieldValueError(
            f"Cannot decode {type(raw_value).__name__} as a linked row."
        )

    def decode_value(self, raw_value: Any) -> list[LinkedRow]:
        if raw_value is None:
            return []
        if isinstance(raw_value, str):
            raw_value = [part.strip() for part in raw_value.split(",") if part.strip()]
        elif isinstance(raw_value, (int, LinkedRow, dict)) and not isinstance(
            raw_value, bool
        ):
            raw_value = [raw_value]
        if not isinstance(raw_value, list):
            raise FieldValueError("A link-row response must be a list.")
        return [self._decode_link(item) for item in raw_value]

    def validate_value(self, value: Any) -> None:
        if value is None:
            raise FieldValidationError(
                "A link-row value cannot be None; use [] to clear it."
            )
        if isinstance(value, bool):
            raise FieldValidationError("A linked row ID cannot be a boolean.")
        if isinstance(value, (int, str, LinkedRow, dict)):
            value = [value]
        if not isinstance(value, list):
            raise FieldValidationError(
                "A link-row value must be an ID, label, returned object, or list."
            )
        for item in value:
            if isinstance(item, LinkedRow):
                continue
            if isinstance(item, bool) or not isinstance(item, (dict, int, str)):
                raise FieldValidationError(
                    "Each linked-row item must be a reference, returned object, "
                    "ID, or label."
                )
            if isinstance(item, dict) and "id" not in item:
                raise FieldValidationError(
                    "A returned linked-row object must contain an 'id'."
                )

    def encode_value(self, value: Any) -> Any:
        self.validate_value(value)
        if isinstance(value, (int, str)) and not isinstance(value, bool):
            return value
        if isinstance(value, (LinkedRow, dict)):
            value = [value]
        encoded = []
        for item in value:
            if isinstance(item, LinkedRow):
                encoded.append(item.id if item.id is not None else item.value)
            elif isinstance(item, dict):
                encoded.append(item["id"])
            else:
                encoded.append(item)
        return encoded

    def get_linked_rows(self) -> list[LinkedRow]:
        """Return selectable related rows with their row IDs and display values."""
        if self.client is None:
            raise FieldDataRetrievalError("Baserow client not provided.")
        try:
            related_table = self.client.get_table(self.link_row_table_id)
            primary_field = related_table.primary_field
            rows = related_table.get_rows(
                include=[primary_field],
                view_id=self.link_row_limit_selection_view_id,
            )
            return [
                LinkedRow(
                    table_id=related_table.id,
                    id=row.id,
                    value=row[primary_field],
                    raw={"id": row.id, "value": row[primary_field]},
                )
                for row in rows
            ]
        except Exception as error:
            raise FieldDataRetrievalError(
                f"Failed to retrieve linked rows for field {self.name!r}."
            ) from error

    def resolve_linked_row(self, label: Any) -> LinkedRow:
        """Resolve one related row by display label, rejecting ambiguity."""
        matches = [row for row in self.get_linked_rows() if row.value == label]
        if not matches:
            raise FieldValidationError(
                f"No linked row with label {label!r} exists for field {self.name!r}."
            )
        if len(matches) > 1:
            raise FieldValidationError(
                f"Label {label!r} is ambiguous for field {self.name!r}; "
                f"it matches {len(matches)} rows."
            )
        return matches[0]
