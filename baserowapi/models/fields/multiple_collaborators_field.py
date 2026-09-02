from typing import Any

from baserowapi.exceptions import FieldValidationError, FieldValueError
from baserowapi.models.fields.field import Field
from baserowapi.models.values import Collaborator


class MultipleCollaboratorsField(Field):
    """Baserow collaborator identity and assignment semantics."""

    TYPE = "multiple_collaborators"
    _COMPATIBLE_FILTERS = [
        "multiple_collaborators_has",
        "multiple_collaborators_has_not",
        "empty",
        "not_empty",
    ]

    @property
    def compatible_filters(self) -> list[str]:
        return self._COMPATIBLE_FILTERS

    @property
    def notify_user_when_added(self) -> bool:
        return self.field_data.get("notify_user_when_added", False)

    @staticmethod
    def _decode_collaborator(raw_value: Any) -> Collaborator:
        if isinstance(raw_value, Collaborator):
            return raw_value
        if not isinstance(raw_value, dict):
            raise FieldValueError("A Baserow collaborator must be an object.")
        collaborator_id = raw_value.get("id")
        if isinstance(collaborator_id, bool) or not isinstance(collaborator_id, int):
            raise FieldValueError(
                "A Baserow collaborator must contain an integer 'id'."
            )
        return Collaborator(
            id=collaborator_id,
            name=raw_value.get("name"),
            email=raw_value.get("email"),
            raw=dict(raw_value),
        )

    def decode_value(self, raw_value: Any) -> list[Collaborator]:
        if raw_value is None:
            return []
        if not isinstance(raw_value, list):
            raise FieldValueError("A collaborators response must be a list.")
        return [self._decode_collaborator(item) for item in raw_value]

    def validate_value(self, value: Any) -> None:
        if not isinstance(value, list):
            raise FieldValidationError("A collaborators value must be a list.")
        for item in value:
            if isinstance(item, Collaborator):
                continue
            if (
                not isinstance(item, dict)
                or isinstance(item.get("id"), bool)
                or not isinstance(item.get("id"), int)
            ):
                raise FieldValidationError(
                    "Each collaborator must be a Collaborator or an object "
                    "with an integer 'id'."
                )

    def encode_value(self, value: Any) -> list[dict[str, int]]:
        self.validate_value(value)
        return [
            {"id": item.id if isinstance(item, Collaborator) else item["id"]}
            for item in value
        ]
