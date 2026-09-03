from typing import Optional

from baserowapi.models.fields.number_field import NumberField


class CountField(NumberField):
    """A read-only relation count returned as a Baserow decimal string."""

    TYPE = "count"

    @property
    def is_read_only(self) -> bool:
        return True

    @property
    def through_field_id(self) -> Optional[int]:
        return self.field_data.get("through_field_id")

    @property
    def formula_type(self) -> Optional[str]:
        return self.field_data.get("formula_type")
