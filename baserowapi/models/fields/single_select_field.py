from typing import Any, Optional

from baserowapi.exceptions import FieldValidationError, FieldValueError
from baserowapi.models.fields._select_options import (
    decode_option,
    decode_options,
    find_option,
    resolve_option,
)
from baserowapi.models.fields.field import Field
from baserowapi.models.values import SelectOption


class SingleSelectField(Field):
    """Baserow metadata and value semantics for a single-select field."""

    TYPE = "single_select"
    _COMPATIBLE_FILTERS = (
        "contains",
        "contains_not",
        "contains_word",
        "doesnt_contain_word",
        "starts_with",
        "single_select_equal",
        "single_select_not_equal",
        "single_select_is_any_of",
        "single_select_is_none_of",
        "empty",
        "not_empty",
    )

    def __init__(self, name: str, field_data: dict[str, Any], client=None) -> None:
        super().__init__(name, field_data, client)
        if not isinstance(field_data.get("select_options"), list):
            raise FieldValidationError(
                "select_options must be a list in single-select field metadata."
            )

    @property
    def options(self) -> list[SelectOption]:
        """Return the configured options without discarding IDs or metadata."""
        return decode_options(self.field_data["select_options"])

    def _get_option_by_id_or_value(
        self, value: int | str
    ) -> Optional[SelectOption]:
        return find_option(self.options, value)

    def resolve_option(self, label: str) -> SelectOption:
        """Resolve one option by label, rejecting missing or duplicate labels."""
        return resolve_option(self.options, label, field_name=self.name)

    def decode_value(self, raw_value: Any) -> Optional[SelectOption]:
        if raw_value is None or isinstance(raw_value, SelectOption):
            return raw_value
        if isinstance(raw_value, dict):
            return decode_option(raw_value)
        if isinstance(raw_value, bool):
            raise FieldValueError("A select option ID cannot be a boolean.")
        if isinstance(raw_value, int):
            known = self._get_option_by_id_or_value(raw_value)
            return known or SelectOption(raw_value, None, raw={"id": raw_value})
        if isinstance(raw_value, str):
            known = self._get_option_by_id_or_value(raw_value)
            return known or SelectOption(None, raw_value, raw={"value": raw_value})
        raise FieldValueError(
            f"Cannot decode {type(raw_value).__name__} as a select option."
        )

    def validate_value(self, value: Any) -> None:
        if value is None or isinstance(value, SelectOption):
            return
        if isinstance(value, bool) or not isinstance(value, (dict, int, str)):
            raise FieldValidationError(
                "A single-select value must be an option, returned object, ID, "
                "label, or None."
            )
        if isinstance(value, dict) and "id" not in value:
            raise FieldValidationError(
                "A returned single-select object must contain an 'id'."
            )

    def encode_value(self, value: Any) -> Any:
        self.validate_value(value)
        if isinstance(value, SelectOption):
            return value.id if value.id is not None else value.value
        if isinstance(value, dict):
            return value["id"]
        return value
