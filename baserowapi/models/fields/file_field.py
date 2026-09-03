from typing import Any

from baserowapi.exceptions import FieldValidationError, FieldValueError
from baserowapi.models.fields.field import Field
from baserowapi.models.values import BaserowFile


class FileField(Field):
    """Baserow file-object and assignment semantics."""

    TYPE = "file"
    _COMPATIBLE_FILTERS = (
        "filename_contains",
        "has_file_type",
        "files_lower_than",
        "empty",
        "not_empty",
    )

    @staticmethod
    def _decode_file(raw_value: Any) -> BaserowFile:
        if isinstance(raw_value, BaserowFile):
            return raw_value
        if isinstance(raw_value, str):
            return BaserowFile(name=raw_value, raw={"name": raw_value})
        if not isinstance(raw_value, dict) or not isinstance(
            raw_value.get("name"), str
        ):
            raise FieldValueError("A Baserow file object must contain a string 'name'.")
        return BaserowFile(
            name=raw_value["name"],
            visible_name=raw_value.get("visible_name"),
            url=raw_value.get("url"),
            size=raw_value.get("size"),
            mime_type=raw_value.get("mime_type"),
            original_name=raw_value.get("original_name"),
            raw=dict(raw_value),
        )

    def decode_value(self, raw_value: Any) -> list[BaserowFile]:
        if raw_value is None:
            return []
        if isinstance(raw_value, str):
            raw_value = [part.strip() for part in raw_value.split(",") if part.strip()]
        if not isinstance(raw_value, list):
            raise FieldValueError("A file-field response must be a list.")
        return [self._decode_file(item) for item in raw_value]

    def validate_value(self, value: Any) -> None:
        if value is None or isinstance(value, str):
            return
        if not isinstance(value, list):
            raise FieldValidationError(
                "A file-field value must be a filename string, list, or None."
            )
        for item in value:
            if isinstance(item, (BaserowFile, str)):
                continue
            if not isinstance(item, dict) or not isinstance(item.get("name"), str):
                raise FieldValidationError(
                    "Each file item must be a BaserowFile, filename, or returned "
                    "object containing 'name'."
                )

    def encode_value(self, value: Any) -> Any:
        self.validate_value(value)
        if value is None or isinstance(value, str):
            return value
        encoded = []
        for item in value:
            if isinstance(item, BaserowFile):
                encoded.append(item.name)
            elif isinstance(item, dict):
                encoded.append(item["name"])
            else:
                encoded.append(item)
        return encoded
