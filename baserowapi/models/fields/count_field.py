from typing import Any, Optional

from baserowapi.models.fields.number_field import NumberField


class CountField(NumberField):
    """A read-only Baserow relation count with number-result semantics."""

    TYPE = "count"
    _COMPATIBLE_FILTERS = [
        "equal",
        "not_equal",
        "contains",
        "contains_not",
        "starts_with",
        "higher_than",
        "higher_than_or_equal",
        "lower_than",
        "lower_than_or_equal",
        "is_even_and_whole",
        "empty",
        "not_empty",
    ]

    def __init__(self, name: str, field_data: dict[str, Any], client=None) -> None:
        super().__init__(name, field_data, client)

    @property
    def is_read_only(self) -> bool:
        return True

    @property
    def through_field_id(self) -> Optional[int]:
        return self.field_data.get("through_field_id")

    @property
    def formula_type(self) -> Optional[str]:
        return self.field_data.get("formula_type")
