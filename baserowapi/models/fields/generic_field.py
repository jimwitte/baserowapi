from typing import Any, Dict, List
from baserowapi.models.fields.field import Field


class GenericField(Field):
    """
    Represents a generic field for unknown or unsupported field types in Baserow.
    """

    TYPE = "generic"

    def __init__(self, name: str, field_data: Dict[str, Any], client=None) -> None:
        super().__init__(name, field_data, client)

    @property
    def compatible_filters(self) -> List[str]:
        return []

    def validate_value(self, value: Any) -> None:
        pass
