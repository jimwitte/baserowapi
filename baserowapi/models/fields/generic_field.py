from typing import Any, Dict, List
from baserowapi.models.fields.field import Field
from baserowapi.models.filter import FilterCompatibility


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

    def filter_compatibility(self, operator: str) -> FilterCompatibility:
        """Unknown field types have no authoritative local filter knowledge."""
        super().filter_compatibility(operator)
        return FilterCompatibility.UNKNOWN
