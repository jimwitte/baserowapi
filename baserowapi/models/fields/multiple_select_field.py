from typing import Any, Optional

from baserowapi.exceptions import FieldValidationError, FieldValueError
from baserowapi.models.fields.field import Field
from baserowapi.models.values import SelectOption


class MultipleSelectField(Field):
    """Baserow metadata and value semantics for a multiple-select field."""

    TYPE = "multiple_select"
    _COMPATIBLE_FILTERS = [
        "contains",
        "contains_not",
        "contains_word",
        "doesnt_contain_word",
        "multiple_select_has",
        "multiple_select_has_not",
        "empty",
        "not_empty",
    ]

    def __init__(self, name: str, field_data: dict[str, Any], client=None) -> None:
        super().__init__(name, field_data, client)
        if not isinstance(field_data.get("select_options"), list):
            raise FieldValidationError(
                "select_options must be a list in multiple-select field metadata."
            )

    @property
    def compatible_filters(self) -> list[str]:
        return self._COMPATIBLE_FILTERS

    @staticmethod
    def _decode_option(raw_value: dict[str, Any]) -> SelectOption:
        if not isinstance(raw_value, dict):
            raise FieldValueError("A Baserow select option must be an object.")
        option_id = raw_value.get("id")
        value = raw_value.get("value")
        if option_id is not None and (
            isinstance(option_id, bool) or not isinstance(option_id, int)
        ):
            raise FieldValueError("A Baserow select option ID must be an integer.")
        if value is not None and not isinstance(value, str):
            raise FieldValueError("A Baserow select option value must be a string.")
        return SelectOption(
            id=option_id,
            value=value,
            color=raw_value.get("color"),
            raw=dict(raw_value),
        )

    @property
    def options(self) -> list[SelectOption]:
        """Return the configured options without discarding IDs or metadata."""
        return [
            self._decode_option(option)
            for option in self.field_data["select_options"]
        ]

    def _get_option_by_id_or_value(
        self, value: int | str
    ) -> Optional[SelectOption]:
        for option in self.options:
            if option.id == value or option.value == value:
                return option
        return None

    def resolve_option(self, label: str) -> SelectOption:
        """Resolve one option by label, rejecting missing or duplicate labels."""
        if not isinstance(label, str):
            raise FieldValidationError("A select option label must be a string.")
        matches = [option for option in self.options if option.value == label]
        if not matches:
            raise FieldValidationError(
                f"No option with label {label!r} exists for field {self.name!r}."
            )
        if len(matches) > 1:
            raise FieldValidationError(
                f"Label {label!r} is ambiguous for field {self.name!r}; "
                f"it matches {len(matches)} options."
            )
        return matches[0]

    def decode_value(self, raw_value: Any) -> list[SelectOption]:
        if raw_value is None:
            return []
        if isinstance(raw_value, str):
            raw_value = [part.strip() for part in raw_value.split(",") if part.strip()]
        if not isinstance(raw_value, list):
            raise FieldValueError("A multiple-select response must be a list.")

        decoded = []
        for item in raw_value:
            if isinstance(item, SelectOption):
                decoded.append(item)
            elif isinstance(item, dict):
                decoded.append(self._decode_option(item))
            elif isinstance(item, bool):
                raise FieldValueError("A select option ID cannot be a boolean.")
            elif isinstance(item, int):
                known = self._get_option_by_id_or_value(item)
                decoded.append(known or SelectOption(item, None, raw={"id": item}))
            elif isinstance(item, str):
                known = self._get_option_by_id_or_value(item)
                decoded.append(known or SelectOption(None, item, raw={"value": item}))
            else:
                raise FieldValueError(
                    f"Cannot decode {type(item).__name__} as a select option."
                )
        return decoded

    def validate_value(self, value: Any) -> None:
        if isinstance(value, str):
            return
        if not isinstance(value, list):
            raise FieldValidationError(
                "A multiple-select value must be a list or comma-separated string."
            )
        for item in value:
            if isinstance(item, SelectOption):
                continue
            if isinstance(item, bool) or not isinstance(item, (dict, int, str)):
                raise FieldValidationError(
                    "Each multiple-select item must be an option, returned object, "
                    "ID, or label."
                )
            if isinstance(item, dict) and "id" not in item:
                raise FieldValidationError(
                    "A returned multiple-select object must contain an 'id'."
                )

    def encode_value(self, value: Any) -> Any:
        self.validate_value(value)
        if isinstance(value, str):
            return value
        encoded = []
        for item in value:
            if isinstance(item, SelectOption):
                encoded.append(item.id if item.id is not None else item.value)
            elif isinstance(item, dict):
                encoded.append(item["id"])
            else:
                encoded.append(item)
        return encoded
