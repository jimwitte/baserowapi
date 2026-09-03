"""Private shared operations for Baserow select-option metadata."""

from typing import Any, Optional

from baserowapi.exceptions import FieldValidationError, FieldValueError
from baserowapi.models.values import SelectOption


def decode_option(raw_value: Any) -> SelectOption:
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


def decode_options(raw_options: list[Any]) -> list[SelectOption]:
    return [decode_option(option) for option in raw_options]


def find_option(
    options: list[SelectOption], value: int | str
) -> Optional[SelectOption]:
    for option in options:
        if option.id == value or option.value == value:
            return option
    return None


def resolve_option(
    options: list[SelectOption], label: str, *, field_name: str
) -> SelectOption:
    if not isinstance(label, str):
        raise FieldValidationError("A select option label must be a string.")
    matches = [option for option in options if option.value == label]
    if not matches:
        raise FieldValidationError(
            f"No option with label {label!r} exists for field {field_name!r}."
        )
    if len(matches) > 1:
        raise FieldValidationError(
            f"Label {label!r} is ambiguous for field {field_name!r}; "
            f"it matches {len(matches)} options."
        )
    return matches[0]
