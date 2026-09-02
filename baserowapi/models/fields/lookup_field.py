from typing import Any, Optional

from baserowapi.exceptions import FieldValueError
from baserowapi.models.fields.field import Field
from baserowapi.models.values import LookupEntry


class LookupField(Field):
    """Baserow lookup metadata and identity-preserving result decoding."""

    TYPE = "lookup"
    _COMPATIBLE_FILTERS = [
        "has_empty_value",
        "has_not_empty_value",
        "has_value_equal",
        "has_not_value_equal",
        "has_value_contains",
        "has_not_value_contains",
        "has_value_contains_word",
        "has_not_value_contains_word",
        "has_value_length_is_lower_than",
    ]

    def __init__(self, name: str, field_data: dict[str, Any], client=None) -> None:
        super().__init__(name, field_data, client)
        if not self.is_read_only:
            raise ValueError("LookupField should be read-only.")

    @property
    def compatible_filters(self) -> list[str]:
        return self._COMPATIBLE_FILTERS

    @property
    def through_field_id(self) -> Optional[int]:
        return self.field_data.get("through_field_id")

    @property
    def through_field_name(self) -> Optional[str]:
        return self.field_data.get("through_field_name")

    @property
    def target_field_id(self) -> Optional[int]:
        return self.field_data.get("target_field_id")

    @property
    def target_field_name(self) -> Optional[str]:
        return self.field_data.get("target_field_name")

    def decode_value(self, raw_value: Any) -> list[LookupEntry]:
        if raw_value is None:
            return []
        if not isinstance(raw_value, list):
            raise FieldValueError("A lookup response must be a list.")
        entries = []
        for item in raw_value:
            if isinstance(item, LookupEntry):
                entries.append(item)
            elif isinstance(item, dict):
                entries.append(
                    LookupEntry(
                        row_id=item.get("id"),
                        value=item.get("value"),
                        raw=dict(item),
                    )
                )
            else:
                entries.append(LookupEntry(row_id=None, value=item, raw=item))
        return entries
