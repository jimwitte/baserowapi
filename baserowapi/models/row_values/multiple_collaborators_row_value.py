from typing import Any, Optional

from baserowapi.exceptions import InvalidRowValueError
from baserowapi.models.fields import MultipleCollaboratorsField
from baserowapi.models.row_values.row_value import RowValue


class MultipleCollaboratorsRowValue(RowValue):
    """Compatibility facade for field-owned collaborator semantics."""

    def __init__(
        self,
        field: MultipleCollaboratorsField,
        raw_value: Optional[Any] = None,
        client: Optional[Any] = None,
    ) -> None:
        super().__init__(field, raw_value if raw_value is not None else [], client)
        if not isinstance(field, MultipleCollaboratorsField):
            raise InvalidRowValueError(
                f"Expected MultipleCollaboratorsField, got {type(field).__name__}."
            )
