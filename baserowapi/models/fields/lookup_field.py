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
        "empty",
        "not_empty",
    ]

    @property
    def compatible_filters(self) -> list[str]:
        return self._COMPATIBLE_FILTERS

    @property
    def is_read_only(self) -> bool:
        return True

    @property
    def formula_type(self) -> Optional[str]:
        return self.field_data.get("formula_type")

    @property
    def array_formula_type(self) -> Optional[str]:
        return self.field_data.get("array_formula_type")

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
