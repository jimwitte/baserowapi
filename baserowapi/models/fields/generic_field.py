from baserowapi.models.fields.field import Field
from baserowapi.models.filter import FilterCompatibility


class GenericField(Field):
    """
    Represents a generic field for unknown or unsupported field types in Baserow.
    """

    TYPE = "generic"

    def filter_compatibility(self, operator: str) -> FilterCompatibility:
        """Unknown field types have no authoritative local filter knowledge."""
        super().filter_compatibility(operator)
        return FilterCompatibility.UNKNOWN
